#!/usr/bin/env python3
"""Render course files for one cluster profile.

Templates live under profiles/templates/, mirroring the repository layout.
Each profile is a TOML file under profiles/. Rendering with the snellius
profile reproduces the published files byte for byte; `--check` proves it.

Template syntax, a small subset of Mustache:
  {{a.b}}          value at dotted path a.b in the innermost context
  {{../a.b}}       the same, one context out (repeat ../ to go further)
  {{a.b:<15}}      a value through a Python format spec
  {{#a.b}}..{{/a.b}}  a list repeats the block per item, a table becomes the
                   innermost context, a true value renders the block once,
                   a false or empty value drops it
  {{^a.b}}..{{/a.b}}  rendered only when a.b is false or empty
  {{#a.b?}}, {{^a.b?}}  the same, but a missing a.b counts as false
Names never fall back to outer contexts: a missing name is an error unless
the section tag ends in `?`. A section tag alone on its line takes the whole
line with it. A string value that holds {{...}} is rendered where it is
used, so profile prose can use profile values.

Usage:
  tools/render_profile.py src                 # writes build/src/
  tools/render_profile.py snellius --check    # diffs against the repo
"""
from __future__ import annotations

import argparse
import copy
import difflib
import math
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILES = ROOT / "profiles"
TEMPLATES = PROFILES / "templates"

# Slurm options a profile may resize, in the order they appear on a command line.
SBATCH_KEYS = [
    ("nodes", "--nodes"),
    ("ntasks", "--ntasks"),
    ("ntasks_per_node", "--ntasks-per-node"),
    ("cpus_per_task", "--cpus-per-task"),
]

# Published files that learners read or run, for lint() beyond the templates.
COURSE_GLOBS = ["README.md", "course-module-*/**/*", "teaching/**/*"]
COURSE_SUFFIXES = {".sh", ".md", ".org", ".py", ".slurm"}

# A name holds no brace, so `\texttt{{{a}}}` reads as `\texttt{` and {{a}}.
TAG = re.compile(r"\{\{([#^/]?)\s*([^{}]+?)\s*\}\}")
STANDALONE = re.compile(r"^[ \t]*(\{\{[#^/][^}]+\}\})[ \t]*(?:\n|\Z)", re.M)
MISSING = object()


# ---------------------------------------------------------------- templates


def parse(text: str) -> list:
    """Turn template text into a tree of str, ("var", name, spec) and
    ("sec", inverted, optional, name, children)."""
    text = STANDALONE.sub(r"\1", text)
    root: list = []
    stack = [(None, root)]
    pos = 0
    for m in TAG.finditer(text):
        if m.start() > pos:
            stack[-1][1].append(text[pos : m.start()])
        kind, body = m.group(1), m.group(2)
        if kind in ("#", "^"):
            name = body.removesuffix("?")
            node = ("sec", kind == "^", body.endswith("?"), name, [])
            stack[-1][1].append(node)
            stack.append((name, node[4]))
        elif kind == "/":
            if stack[-1][0] != body.removesuffix("?"):
                raise ValueError(f"{{{{/{body}}}}} closes {stack[-1][0]!r}")
            stack.pop()
        else:
            name, _, spec = body.partition(":")
            stack[-1][1].append(("var", name.strip(), spec))
        pos = m.end()
    if len(stack) != 1:
        raise ValueError(f"unclosed section {stack[-1][0]!r}")
    if pos < len(text):
        root.append(text[pos:])
    return root


def lookup(stack: list, name: str):
    """The value of `name` in the innermost context, or `../` contexts out.
    Returns MISSING instead of searching outer contexts."""
    depth = 0
    while name.startswith("../"):
        depth, name = depth + 1, name[3:]
    if depth >= len(stack):
        raise KeyError(f"{'../' * depth}{name} goes past the outermost context")
    value = stack[-1 - depth]
    if name == ".":
        return value
    for part in name.split("."):
        if not isinstance(value, dict) or part not in value:
            return MISSING
        value = value[part]
    return value


def render_tree(tree: list, stack: list) -> str:
    out = []
    for node in tree:
        if isinstance(node, str):
            out.append(node)
        elif node[0] == "var":
            _, name, spec = node
            value = lookup(stack, name)
            if value is MISSING:
                raise KeyError(f"no value for {{{{{name}}}}}")
            if isinstance(value, str) and "{{" in value:
                value = render(value, stack)
            out.append(format(value, spec))
        else:
            _, inverted, optional, name, children = node
            value = lookup(stack, name)
            if value is MISSING and not optional:
                raise KeyError(f"no value for section {name!r}; end the tag in ? if it is optional")
            empty = value is MISSING or not value
            if inverted:
                if empty:
                    out.append(render_tree(children, stack))
            elif empty:
                continue
            elif isinstance(value, list):
                for item in value:
                    out.append(render_tree(children, stack + [item]))
            elif isinstance(value, dict):
                out.append(render_tree(children, stack + [value]))
            else:
                out.append(render_tree(children, stack))
    return "".join(out)


def render(text: str, stack: list) -> str:
    return render_tree(parse(text), stack)


# ---------------------------------------------------------------- profiles


def load_profiles() -> dict:
    return {p.stem: tomllib.loads(p.read_text()) for p in sorted(PROFILES.glob("*.toml"))}


def override(job: dict, base: dict | None) -> str:
    """The sbatch options that turn the base profile's job into this one."""
    base = base or {}
    return " ".join(
        f"{flag}={job[key]}"
        for key, flag in SBATCH_KEYS
        if key in job and job[key] != base.get(key)
    )


def table_lines(table: dict) -> list:
    """Markdown table rows for an empty results table, as {"line": ...}."""
    width = table["first_col_width"]
    heads = [table["first_col"]] + table["columns"]

    def row(first: str, cells: list) -> str:
        head = (" " + first.ljust(width) + " ")[: width + 2]
        return "|" + "|".join([head] + cells) + "|"

    lines = [
        row(heads[0], [f" {h} " for h in heads[1:]]),
        "|" + "|".join("-" * (len(h) + 2) if i else "-" * (width + 2) for i, h in enumerate(heads)) + "|",
    ]
    lines += [row(size, [" " * (len(h) + 2) for h in heads[1:]]) for size in table["sizes"]]
    return [{"line": line} for line in lines]


def derive(profile: dict, base: dict | None) -> dict:
    """Add computed fields: sbatch overrides against `base`, table rows."""
    prof = copy.deepcopy(profile)
    for module, jobs in prof.get("jobs", {}).items():
        base_jobs = (base or {}).get("jobs", {}).get(module, {})
        for name, job in jobs.items():
            job["override"] = override(job, base_jobs.get(name))
            if "sample_n" in job:
                # Rank 0 holds the remainder element first, as in the C codes.
                n, world = job["sample_n"], job.get("ntasks", 1)
                job["local_n"] = n // world + (1 if n % world else 0)
            if "script" in job:
                parts = ["sbatch", job["override"], job["script"], str(job.get("example_n", "<N>"))]
                job["cmd"] = " ".join(p for p in parts if p)
    nodes = prof.get("system", {}).get("nodes")
    if nodes:
        prof["system"]["node_count"] = len(nodes)
        prof["system"]["total_cpus"] = sum(n["cpus"] for n in nodes)
        shapes = {}
        for n in nodes:
            shapes[n["cpus"]] = shapes.get(n["cpus"], 0) + 1
        prof["system"]["node_shapes"] = " and ".join(
            f"{count} with {cpus} cores" for cpus, count in shapes.items())
    for section in prof.values():
        if isinstance(section, dict):
            for value in section.values():
                if isinstance(value, dict) and "columns" in value and "sizes" in value:
                    value["lines"] = table_lines(value)
    return prof


def context(name: str, profiles: dict) -> dict:
    ctx = derive(profiles[name], None)
    # Notes about other clusters: each one's profile, with its jobs written as
    # overrides of this profile's jobs.
    ctx["asides"] = [derive(profiles[o], profiles[name]) for o in ctx.get("render", {}).get("asides", [])]
    return ctx


# ---------------------------------------------------------------- checks


def job_problems(where: str, job: dict, limits: dict) -> list:
    """Problems with one job's size against Slurm and the profile's limits.
    `job` has any of nodes, ntasks, ntasks_per_node and cpus_per_task."""
    problems = []
    per_node = limits.get("max_cpus_per_node")
    max_nodes = limits.get("max_nodes")
    nodes = job.get("nodes", 1)
    ntasks = job.get("ntasks", 1)
    pinned = job.get("ntasks_per_node")
    if pinned and ntasks > nodes * pinned:
        problems.append(f"{where} asks {ntasks} tasks on {nodes} nodes at {pinned} per node")
    if nodes > 1 and ntasks > nodes and not pinned:
        # Slurm may fill one large node first, so the per-node count below
        # holds only when the job pins it.
        problems.append(f"{where} spreads {ntasks} tasks over {nodes} nodes without --ntasks-per-node")
    tasks = pinned or math.ceil(ntasks / nodes)
    cpus = tasks * job.get("cpus_per_task", 1)
    if per_node and cpus > per_node:
        problems.append(f"{where} asks {cpus} CPUs per node, limit {per_node}")
    if max_nodes and nodes > max_nodes:
        problems.append(f"{where} asks {nodes} nodes, limit {max_nodes}")
    return problems


def validate(name: str, profile: dict) -> list:
    """Problems with a profile's job sizes, against Slurm and its own limits."""
    limits = profile.get("limits", {})
    return [
        problem
        for module, jobs in profile.get("jobs", {}).items()
        for job_name, job in jobs.items()
        for problem in job_problems(f"{name}: jobs.{module}.{job_name}", job, limits)
    ]


# One #SBATCH line: the option and its value, as --opt=v, --opt v or -o v.
SBATCH_LINE = re.compile(r"^#SBATCH\s+(--?[A-Za-z-]+)(?:[=\s]\s*([^\s#]+))?")
SBATCH_OPTS = {
    "-N": "nodes", "--nodes": "nodes",
    "-n": "ntasks", "--ntasks": "ntasks",
    "--ntasks-per-node": "ntasks_per_node",
    "-c": "cpus_per_task", "--cpus-per-task": "cpus_per_task",
    "-C": "constraint", "--constraint": "constraint",
}


def sbatch_blocks(text: str) -> list:
    """Each run of consecutive #SBATCH lines, as (first line number,
    options). Sizes are ints; a placeholder such as `--nodes=#` is left out."""
    blocks, start, opts = [], None, {}
    for i, line in enumerate(text.splitlines() + [""], 1):
        m = SBATCH_LINE.match(line)
        if not m:
            if start is not None:
                blocks.append((start, opts))
                start = None
            continue
        if start is None:
            start, opts = i, {}
        key, value = SBATCH_OPTS.get(m.group(1)), m.group(2)
        if key and value:
            opts[key] = value if key == "constraint" else int(value) if value.isdigit() else None
    return blocks


def check_scripts(name: str, profile: dict, files: dict) -> list:
    """Problems with the #SBATCH blocks in rendered files: the same size
    rules as validate(), and constraints the profile does not list."""
    limits = profile.get("limits", {})
    allowed = set(profile.get("slurm", {}).get("constraints", []))
    problems = []
    for path, text in files.items():
        for line, opts in sbatch_blocks(text):
            where = f"{name}: {path}:{line}"
            size = {k: v for k, v in opts.items() if k != "constraint" and v is not None}
            problems += job_problems(where, size, limits)
            if "constraint" in opts and opts["constraint"] not in allowed:
                problems.append(f"{where} asks for constraint {opts['constraint']}, which {name} lacks")
    return problems


def course_files(root: Path, skip=()) -> dict:
    """Published course files under `root` that no template produces.

    Learners on every cluster get these files as they are, so a profile's
    module rules have to hold for them too."""
    found = {}
    for pattern in COURSE_GLOBS:
        for path in sorted(root.glob(pattern)):
            rel = str(path.relative_to(root))
            if not path.is_file() or rel in skip:
                continue
            # Scripts such as hands-on/compilepi have a shebang and no suffix.
            if path.suffix in COURSE_SUFFIXES or (not path.suffix and path.read_bytes()[:2] == b"#!"):
                found[rel] = path.read_text(errors="replace")
    return found


def lint(profile: dict, files: dict) -> list:
    """Lines the profile's module rules forbid, as 'path:line: text'.
    Pass the rendered templates and course_files() for the rest."""
    mods = profile.get("modules", {})
    if not mods.get("stack_on_own_line"):
        return []
    stack = re.escape(mods["stack"])
    # An optional shell prompt, then a second module on the same line; a
    # `&&` or `;` starts a new command, which is fine.
    one_line = re.compile(rf"^\s*(?:\[[^\]]*\]\$\s+|\S*\$\s+)?module\s+load\s+{stack}\s+(?![&;|#])\S")
    # Prose that names both in one code span, such as "Load =2025 foss/2025a="
    # on a slide, reads as one command too.
    in_prose = re.compile(rf"\bload\s+[=`~]{stack}\s+[\w/]", re.I)
    return [
        f"{path}:{i}: {line.strip()}"
        for path, text in files.items()
        for i, line in enumerate(text.splitlines(), 1)
        if one_line.match(line) or in_prose.search(line)
    ]


def check(name: str, rendered: dict, against: Path, whole_tree: bool) -> int:
    """Compare a render with a tree: content, executable bit, missing files,
    and with `whole_tree` files the render does not produce. Returns the
    number of problems and prints a diff and a summary."""
    bad = 0
    for rel, text in rendered.items():
        target = against / rel
        if not target.is_file():
            bad += 1
            print(f"missing: {rel}")
            continue
        have = target.read_text()
        if have != text:
            bad += 1
            sys.stdout.writelines(difflib.unified_diff(
                have.splitlines(True), text.splitlines(True), f"a/{rel}", f"b/{rel}"))
            continue
        # Git keeps only the executable bit, so compare that.
        want_x = bool((TEMPLATES / rel).stat().st_mode & 0o100)
        have_x = bool(target.stat().st_mode & 0o100)
        if want_x != have_x:
            bad += 1
            print(f"mode: {rel} executable={have_x}, template executable={want_x}")
    extra = []
    if whole_tree:
        extra = sorted(
            str(p.relative_to(against)) for p in against.rglob("*")
            if p.is_file() and str(p.relative_to(against)) not in rendered)
        for rel in extra:
            print(f"extra: {rel}")
    summary = f"{name}: {len(rendered) - bad}/{len(rendered)} files identical"
    if extra:
        summary += f", {len(extra)} extra"
    print(summary, file=sys.stderr)
    return bad + len(extra)


# ---------------------------------------------------------------- driver


def render_all(name: str) -> dict:
    profiles = load_profiles()
    if name not in profiles:
        sys.exit(f"no profile {name!r}; have " + ", ".join(profiles))
    ctx = context(name, profiles)
    return {
        str(t.relative_to(TEMPLATES)): render(t.read_text(), [ctx])
        for t in sorted(TEMPLATES.rglob("*"))
        if t.is_file()
    }


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("profile")
    ap.add_argument("--out", type=Path, help="output root (default build/PROFILE)")
    ap.add_argument("--check", action="store_true", help="diff against --against instead of writing")
    ap.add_argument("--against", type=Path, default=ROOT,
                    help="tree --check compares with (default: repo); any other tree "
                         "must hold only rendered files")
    args = ap.parse_args(argv)

    profiles = load_profiles()
    problems = validate(args.profile, profiles.get(args.profile, {}))
    rendered = render_all(args.profile)
    problems += check_scripts(args.profile, profiles[args.profile], rendered)
    files = course_files(ROOT, skip=rendered)
    files.update(rendered)
    problems += lint(profiles[args.profile], files)
    for p in problems:
        print(f"error: {p}", file=sys.stderr)
    # Published files that no template covers yet go to every cluster as
    # they are; report their oversized jobs without failing the render.
    untemplated = {k: v for k, v in files.items() if k not in rendered}
    for w in check_scripts(args.profile, profiles[args.profile], untemplated):
        print(f"warning: {w} (no template yet)", file=sys.stderr)

    if args.check:
        # The repository also holds files no template produces, so only a
        # render tree is checked for extra files.
        whole_tree = args.against.resolve() != ROOT
        bad = check(args.profile, rendered, args.against, whole_tree)
        return 1 if bad or problems else 0

    out = args.out or ROOT / "build" / args.profile
    for rel, text in rendered.items():
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        target.chmod((TEMPLATES / rel).stat().st_mode & 0o777)
    print(f"{args.profile}: wrote {len(rendered)} files to {out}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
