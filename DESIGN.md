# Cluster profiles

Internal design note for ljos eessi-r2ag (parent eessi-2wmy). Branch
`feat/cluster-profiles`, off the class branch at 7dcd0fe.

## Problem

The course is written for Snellius. For the SRC course cluster we added
hand-written notes ("On an SRC cluster, ...") and override tables to every
module. Those notes drift: the hybrid README still says three workspaces and
the fundamentals slide says 16 cores, while the cluster now has four nodes and
66 CPUs. INVENTORY.md lists the 52 values that differ between clusters.

## Decision

1. One TOML file per cluster under `profiles/`: `snellius.toml`, `src.toml`.
2. Files that vary get a template under `profiles/templates/`, at the same
   path as the published file. Placeholders are a small Mustache subset.
3. `tools/render_profile.py PROFILE` renders every template. Standard library
   only (`tomllib`, Python 3.11+).
4. The published files stay in place and are the Snellius render.
   `render_profile.py snellius --check` must report every file identical.
5. Other profiles render to `build/PROFILE/` (ignored by git). SRC notes and
   override tables come from fields in `src.toml`, not from prose in the
   published files.

## Alternatives weighed

- **sbatch overrides only.** Keep the scripts and generate a table of
  `sbatch --ntasks=...` lines per profile. Zero template risk, and the
  renderer already does this for the asides (`jobs.*.cmd`). But it cannot fix
  module lines, partitions, paths or the README tables, and learners have to
  type the override right. Kept as one output, not the whole design.
- **Org `#+MACRO` driven by the profile.** Works for slides only, needs a
  setup file at export time, and changes the published `.org` source (every
  `rome` becomes `{{{cpu_partition}}}`). Rejected: the same templates cover
  Org, Markdown and shell, and the Snellius `.org` stays byte-identical.
- **Jinja2.** Full language, but a dependency, and its whitespace control
  makes byte-identical output harder to reason about. The subset needed here
  is about 60 lines.

## Profile schema

Every key is optional unless a template uses it; a template that names a
missing key fails the render. A value that is not checked carries a
`# unverified` comment.

| Table | Keys | Meaning |
|---|---|---|
| `[profile]` | `name`, `description`, `verified` | identity, date the facts were checked |
| `[render]` | `asides` | other profiles whose notes appear in this render (Snellius: `["src"]`) |
| `[system]` | `name`, `login_host`, `login_nodes`, `ondemand_url`, `ondemand_apps`, `interconnect` | prose facts |
| `[[system.nodes]]` | `name`, `cpus`, `mem_mb`, `gres` | one entry per node; renderer derives `system.node_count`, `system.total_cpus` |
| `[[system.partition_info]]` | `name`, `nodes`, `cpus_per_node`, `gpus_per_node`, `gpu_model` | partition catalogue for large systems |
| `[partitions]` | `cpu`, `cpu_alt`, `gpu`, ... | logical role to partition name |
| `[slurm]` | `default_partition`, `def_mem_per_cpu_mb`, `oversubscribe`, `gpu_request`, `mail`, `constraints` | scheduler facts |
| `[limits]` | `max_cpus_per_node`, `max_nodes` | course sizing rule; the renderer checks every job against it |
| `[modules]` | `stack`, `toolchain`, `compiler`, `python`, `qcg`, `site_modulepath`, `stack_on_own_line` | module names; with `stack_on_own_line` the renderer rejects `module load 2025 X` |
| `[paths]` | `home`, `scratch_shared`, `scratch_link`, `scratch_node`, `projects`, `archive`, `tmpdir` | file systems |
| `[tools]` | `myquota`, `accinfo`, `ear`, `uprof`, `papi`, `perf`, `seff` | booleans for sections that only make sense where the tool exists |
| `[accounting]` | `unit`, `sbu_per_core_hour` | SBU or core-hours |
| `[jobs.MODULE.JOB]` | `nodes`, `ntasks`, `ntasks_per_node`, `cpus_per_task`, `script`, `example_n`, `sample_n` | job sizes; renderer derives `override`, `cmd`, `local_n` |
| `[MODULE]` | free-form, e.g. `hybrid.table`, `hybrid.table_note`, `hybrid.aside_note` | module-specific text and tables |

Derived fields, computed before rendering:

- `jobs.M.J.override`: the sbatch options that turn the rendering profile's
  job into this profile's job, in the order nodes, ntasks, ntasks-per-node,
  cpus-per-task. Only meaningful inside an aside.
- `jobs.M.J.cmd`: `sbatch <override> <script> <example_n>`.
- `jobs.M.J.local_n`: rank 0's share of `sample_n`, as the C codes print it.
- `X.table.lines`: Markdown rows for any table with `columns` and `sizes`,
  padded the way the published tables are.

## Template conventions

- `{{a.b}}` inserts a value; `{{a.b:<15}}` passes it through a Python format
  spec, which keeps the `#SBATCH ... # comment` columns aligned.
- `{{#a.b}}...{{/a.b}}` repeats over a list, scopes into a table, or renders
  once for a true value. `{{^a.b}}...{{/a.b}}` renders when the value is false,
  empty or missing.
- A section tag alone on a line removes that line.
- A string value that contains `{{` is rendered in the current scope, so
  profile prose can say `{{limits.max_cpus_per_node}}` or `{{script}}`.
- Templates exist only for files that vary. No published file contains `{{`
  today; `.tex` files could, so check before templating one.
- Keep cluster names out of `if` logic. Prefer a fact (`tools.myquota`) over
  a profile name.

## Workflow

```
python3 tools/render_profile.py snellius --check   # published files unchanged?
python3 tools/render_profile.py src                # build/src/...
python3 tools/test_render.py                       # round trip, limits, lint
```

To change a published file that has a template: edit the template, render
with `--out .` for Snellius, commit both. CI can run `--check` and the tests.

## Slides

The Org sources render the same way as Markdown. The SRC slide in
fundamentals (`fundamentals-of-hpc.org:1727-1732`) becomes a block filled from
`src.toml` (`system.nodes`, `paths`, `tools`), shown in the Snellius render as
an aside and in the SRC render as the cluster description. Job-script slides
(`:2143`, `:2215`, `:2389`, `:2871`) take `partitions.cpu` and per-slide
`jobs.fundamentals.*` sizes. The compile step reads the rendered `.org`
(`build/src/.../slides/`) instead of the source. Slide geometry (`#+attr_latex`
positions) does not change, so text length matters: keep SRC values short.

## Migration plan

One module per commit, each with `snellius --check` green:

1. `course-module-snellius-hybrid-jobs`: done in this branch.
2. `course-module-qcg-pilotjob`: job sizes (16 → 2, example 3's 2×128),
   arrays, the `module use` site path (`modules.site_modulepath`, empty on
   Snellius) and the SBU text (`accounting`). The scripts now hard-code the
   SRC course CVMFS path, so they do not run on Snellius as published.
3. `course-module-fundamentals-of-hpc`: `hands-on.md` partitions, GPU job,
   `myquota`/`accinfo` rows, the SRC slide and slide job scripts.
4. `course-module-snellius-fs`: paths and the scratch-node constraint; the
   recorded Snellius output stays as it is.
5. `course-module-performance-analysis`: `hwperf`, EAR and uProf sections
   behind `tools.*`.
6. Top-level README note from `src.toml`.

## Open questions for Rohit

1. The Snellius render carries the SRC asides because the published files
   do. Should upstream keep them, or should the Snellius render drop them
   (`render.asides = []`) and SRC learners get the `build/src` copy instead?
2. Where do SRC learners get the SRC render: a generated branch, a release
   archive, or a `make src` in the class checkout?
3. The SRC aside still says three workspaces, and ex4's override has no
   `--ntasks-per-node=2`, so with coursenode4r600 in the partition Slurm may
   put four of the six tasks on that node. The last commit on this branch
   fixes both in `src.toml` and regenerates the README. Keep it or drop it?
4. `[limits]` encodes today's course rule (two per node). Should the 60-core
   node count as a separate shape, so a profile can offer a "big node"
   variant (for example 16 tasks on coursenode4r600)?
5. Snellius facts marked `# unverified` (mail, default partition, memory per
   node, QCG module name, EESSI init path): worth one check on Snellius before
   upstreaming?
6. Should profiles describe one deployment (the Maastricht course) or a class of
   clusters (any SRC Magic Castle), with the node list filled from `sinfo`?
