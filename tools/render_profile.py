#!/usr/bin/env python3
"""Render course files for one cluster profile.

Templates live under profiles/templates/, mirroring the repository layout.
Each profile is a TOML file under profiles/. Rendering with the snellius
profile reproduces the published files byte for byte; `--check` proves it.

Template syntax, a small subset of Mustache:
  {{a.b}}          value at dotted path a.b
  {{a.b:<15}}      the same, through a Python format spec
  {{#a.b}}..{{/a.b}}  a list repeats the block per item, a true value
                   renders it once, a false or missing value drops it
  {{^a.b}}..{{/a.b}}  rendered only when a.b is false, empty or missing
A section tag alone on its line takes the whole line with it. A string value
that itself holds {{...}} is rendered in the current context, so profile
prose can use profile values.

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

TAG = re.compile(r"\{\{([#^/]?)\s*([^}]+?)\s*\}\}")
STANDALONE = re.compile(r"^[ \t]*(\{\{[#^/][^}]+\}\})[ \t]*(?:\n|\Z)", re.M)
MISSING = object()


# ---------------------------------------------------------------- templates


def parse(text: str) -> list:
    """Turn template text into a tree of str, ("var", name, spec) and
    ("sec", inverted, name, children)."""
    text = STANDALONE.sub(r"\1", text)
    root: list = []
    stack = [(None, root)]
    pos = 0
    for m in TAG.finditer(text):
        if m.start() > pos:
            stack[-1][1].append(text[pos : m.start()])
        kind, body = m.group(1), m.group(2)
        if kind in "#^" and kind:
            node = ("sec", kind == "^", body, [])
            stack[-1][1].append(node)
            stack.append((body, node[3]))
        elif kind == "/":
            if stack[-1][0] != body:
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
    if name == ".":
        return stack[-1]
    first, *rest = name.split(".")
    for frame in reversed(stack):
        if isinstance(frame, dict) and first in frame:
            value = frame[first]
            for part in rest:
                if not isinstance(value, dict) or part not in value:
                    return MISSING
                value = value[part]
            return value
    return MISSING


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
            _, inverted, name, children = node
            value = lookup(stack, name)
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


def validate(name: str, profile: dict) -> list:
    """Problems with a profile's job sizes against its own limits."""
    problems = []
    limits = profile.get("limits", {})
    per_node = limits.get("max_cpus_per_node")
    max_nodes = limits.get("max_nodes")
    for module, jobs in profile.get("jobs", {}).items():
        for job_name, job in jobs.items():
            nodes = job.get("nodes", 1)
            tasks = job.get("ntasks_per_node") or math.ceil(job.get("ntasks", 1) / nodes)
            cpus = tasks * job.get("cpus_per_task", 1)
            where = f"{name}: jobs.{module}.{job_name}"
            if per_node and cpus > per_node:
                problems.append(f"{where} asks {cpus} CPUs per node, limit {per_node}")
            if max_nodes and nodes > max_nodes:
                problems.append(f"{where} asks {nodes} nodes, limit {max_nodes}")
    return problems


def lint(profile: dict, rendered: dict) -> list:
    """Lines the profile's module rules forbid, as 'path:line: text'."""
    mods = profile.get("modules", {})
    if not mods.get("stack_on_own_line"):
        return []
    one_line = re.compile(rf"^\s*module load {re.escape(mods['stack'])}\s+[^\s#]")
    return [
        f"{path}:{i}: {line.strip()}"
        for path, text in rendered.items()
        for i, line in enumerate(text.splitlines(), 1)
        if one_line.match(line)
    ]


# ---------------------------------------------------------------- driver


def render_all(name: str) -> dict:
    profiles = load_profiles()
    if name not in profiles:
        sys.exit(f"no profile {name!r}; have {', '.join(profiles)}")
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
    ap.add_argument("--against", type=Path, default=ROOT, help="tree --check compares with (default: repo)")
    args = ap.parse_args(argv)

    profiles = load_profiles()
    problems = validate(args.profile, profiles.get(args.profile, {}))
    rendered = render_all(args.profile)
    problems += lint(profiles[args.profile], rendered)
    for p in problems:
        print(f"error: {p}", file=sys.stderr)

    if args.check:
        bad = 0
        for rel, text in rendered.items():
            target = args.against / rel
            have = target.read_text() if target.exists() else ""
            if have != text:
                bad += 1
                sys.stdout.writelines(difflib.unified_diff(
                    have.splitlines(True), text.splitlines(True), f"a/{rel}", f"b/{rel}"))
        print(f"{args.profile}: {len(rendered) - bad}/{len(rendered)} files identical", file=sys.stderr)
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
