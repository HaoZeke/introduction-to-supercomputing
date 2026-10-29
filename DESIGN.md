# Cluster profiles

Design note for the cluster profiles. Branch `feat/cluster-profiles`, on
the class branch at 389d29a.

## Problem

The course is written for Snellius. For the SRC course cluster we added
hand-written notes ("On an SRC cluster, ...") and override tables to every
module. Those notes drift: the hybrid README said three workspaces and
the fundamentals slide said 16 cores, while the cluster has four nodes and
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
`# unverified` comment. Keys in *italics* are recorded, not rendered yet:
no template or check reads them today.

| Table | Keys | Meaning |
|---|---|---|
| `[profile]` | *`name`*, *`description`*, *`verified`* | identity, date the facts were checked |
| `[render]` | `asides` | other profiles whose notes appear in this render (Snellius: `["src"]`) |
| `[system]` | `name`, `interconnect`, *`login_host`*, *`login_nodes`*, *`ondemand_url`*, *`ondemand_apps`*, *`peak_pflops`* | prose facts |
| `[[system.nodes]]` | `cpus`, *`name`*, *`mem_mb`*, *`gres`* | one entry per node; renderer derives `system.node_count`, `system.total_cpus`, `system.node_shapes` |
| `[[system.partition_info]]` | *`name`*, *`nodes`*, *`cpus_per_node`*, *`gpus_per_node`*, *`gpu_model`* | partition catalogue for large systems |
| `[partitions]` | `cpu`, `gpu`, `real_gpu_node`, *`cpu_alt`*, *`gpu_alt`*, *`fat`*, *`staging`*, *`default`* | logical role to partition name |
| `[slurm]` | `mail`, `def_mem_per_cpu_mb`, `constraints`, *`default_partition`*, *`oversubscribe`*, *`gpu_request`*, *`select`*, *`min_allocation_cpus`*, *`min_allocation_mem_gib`* | scheduler facts; `constraints` lists the `--constraint` values a job script may ask for |
| `[limits]` | `max_cpus_per_node`, `max_nodes` | course sizing rule; the renderer checks every profile job and every rendered job script against it |
| `[modules]` | `stack`, `toolchain`, `stack_on_own_line`, *`compiler`*, *`python`*, *`qcg`*, *`site_modulepath`*, *`uprof`*, *`eessi_versions`*, *`r`* | module names; with `stack_on_own_line` the renderer rejects `module load 2025 X` |
| `[paths]` | `home_link`, `scratch_node`, `scratch_user`, `shared_fs`, *`home`*, *`scratch_shared`*, *`scratch_link`*, *`scratch_local`*, *`scratch_local_real`*, *`projects`*, *`archive`*, *`tmpdir`* | file systems; the file systems README uses `scratch_user` in place of `/scratch-shared` where it is set, and shows the scratch-node constraint only where `scratch_node` is set |
| `[tools]` | `myquota`, `accinfo`, *`ear`*, *`uprof`*, *`papi`*, *`perf`*, *`seff`*, *`mpifileutils`* | booleans for sections that only make sense where the tool exists |
| `[accounting]` | *`unit`*, *`sbu_per_core_hour`* | SBU or core-hours |
| `[jobs.MODULE.JOB]` | `nodes`, `ntasks`, `ntasks_per_node`, `cpus_per_task`, `script`, `example_n`, `sample_n` | job sizes; renderer derives `override`, `cmd`, `local_n`. `jobs.fundamentals` holds the hands-on jobs (`hello`, `pi`) and the slide jobs (`first`, `mpi`, `mpi_compare`, `firsttest`, `r`) |
| `[MODULE]` | free-form, e.g. `hybrid.table`, `hybrid.aside_note`, `hybrid.example_source`, `fundamentals.mpi_compare_a`, `fundamentals.mpi_compare_b`, `fs.share` | module-specific text and tables; `mpi_compare_a` and `_b` are the slide's prompt to change the job size |

Derived fields, computed before rendering:

- `jobs.M.J.override`: the sbatch options that turn the rendering profile's
  job into this profile's job, in the order nodes, ntasks, ntasks-per-node,
  cpus-per-task. Templates use it only inside an aside. When the base job
  sets an option this job leaves out, the render fails, since the override
  cannot unset it.
- `jobs.M.J.cmd`: `sbatch <override> <script> <example_n>`.
- `jobs.M.J.local_n`: rank 0's share of `sample_n`, as the C codes print it.
- `X.table.lines`: Markdown rows for any table with `columns` and `sizes`,
  padded the way the published tables are.

## Template conventions

- `{{a.b}}` inserts a value; `{{a.b:<15}}` passes it through a Python format
  spec, which keeps the `#SBATCH ... # comment` columns aligned.
- `{{#a.b}}...{{/a.b}}` repeats over a list, scopes into a table, or renders
  once for a true value. `{{^a.b}}...{{/a.b}}` renders when the value is false
  or empty.
- Names resolve in the innermost scope only. Inside `{{#jobs.hybrid.ex2}}`,
  `{{ntasks}}` is the job's and `{{../modules.stack}}` is the profile's. A
  name that is not there is an error; nothing falls back to an outer scope.
- A section on an optional key ends in `?`: `{{#ntasks_per_node?}}` drops its
  block when the job has no such key. Without `?` a missing key is an error.
- A section tag alone on a line removes that line.
- A string value that contains `{{` is rendered where it is used, so
  profile prose can say `{{limits.max_cpus_per_node}}` or `{{script}}`. The
  `../` depth then depends on the tag that inserts it.
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

`--check` compares content and the executable bit (the only mode Git keeps)
and reports missing files. Against a render tree (`--against build/src`) it
also reports files no template produced. Against the repository it does not,
since most published files have no template. Every run also lints the render
and the untemplated course files (`README.md`, and `.sh`, `.md`, `.org`,
`.py`, `.slurm` and scripts with a shebang and no suffix under
`course-module-*` and `teaching/`) against the profile's module rules.

Every run checks the jobs twice. `validate()` checks each
`[jobs.MODULE.JOB]` in the profile against `[limits]`, and rejects a
multi-node job with more tasks than nodes and no `ntasks_per_node`, since
Slurm may then pack it unevenly. `check_scripts()` reads every `#SBATCH`
block in the rendered files and applies the same rules, plus
`slurm.constraints`. A problem in either fails the render. The same check
over untemplated course files prints a warning ending in "(no template
yet)" and does not fail: those files reach every cluster as published
until a template covers them. Today the SRC render warns about the QCG
Pilot Job and workflow scripts, which ask for 16 or 128 CPUs per node.

## Slides

The Org sources render the same way as Markdown. The SRC slide in
fundamentals (`fundamentals-of-hpc.org:1727-1732`) becomes a block filled from
`src.toml` (`system.nodes`, `paths`, `tools`), shown in the Snellius render as
an aside and in the SRC render as the cluster description. Job-script slides
(`:2144`, `:2216`, `:2390`, `:2872`) take `partitions.cpu` and per-slide
`jobs.fundamentals.*` sizes, and the two dependency jobs (`:2267`, `:2284`)
take `partitions.cpu`. The compile step reads the rendered `.org`
(`build/src/.../slides/`) instead of the source. Slide geometry (`#+attr_latex`
positions) does not change, so text length matters: keep SRC values short.

## Migration plan

One module per commit, each with `snellius --check` green:

1. `course-module-snellius-hybrid-jobs`: done in this branch.
2. `course-module-qcg-pilotjob`: job sizes (16 → 2, example 3's 2×128),
   arrays, the `module use` site path (`modules.site_modulepath`, empty on
   Snellius) and the SBU text (`accounting`). The scripts now hard-code the
   SRC course CVMFS path, so they do not run on Snellius as published.
3. `course-module-fundamentals-of-hpc`: templates cover `hands-on.md`
   (hello and pi sizes, GPU partition, login note), `hands-on/pi.sh`, the
   course cluster slide, the slide job scripts and the slide's mail boxes.
   Still open: `hands-on/README.md`.
4. `course-module-snellius-fs`: a template covers the cluster note, the
   scratch-node constraint and the `/scratch-shared` commands, which the
   SRC render replaces with `paths.scratch_user`. Still open: the other
   paths. The recorded Snellius output stays.
5. `course-module-performance-analysis`: `hwperf`, EAR and uProf sections
   behind `tools.*`.
6. Top-level README note from `src.toml`.

## SSH pass findings

Findings from a pass over the SRC course cluster by SSH on 2026-10-28. A
course bug gets a fix in the published source and is a candidate for a
standalone upstream fix. A cluster fact moves into the profiles.

| Finding | Kind | Where it went |
|---|---|---|
| U+00A0 in QC example_01/array_job.sh | course bug | published file |
| `Load =2025 foss/2025a=` on the mpirun slide | course bug | published slide; lint catches the pattern |
| `myquota` called Snellius-only | cluster fact | `tools.myquota` in the SRC login note |
| `gpu_a100` partition | cluster fact | `partitions.gpu`, `fundamentals.gpu_result`, `fundamentals.gpu_aside` |
| 16 and 32 CPU requests | cluster fact | `jobs.fundamentals.hello`, `.pi` |
| Slurm mail options | cluster fact | `slurm.mail` drops the slide's mail boxes |
| home symlink, `du -sh ~` prints 512 | cluster fact | `paths.home_link` in the file systems note |
| no mpifileutils | cluster fact | `tools.mpifileutils`; no course file uses it yet |
| S1.12 timeout | neither | the slide asks "Can you solve the error?"; the 1-minute limit against `sleep 120` is the error to solve, as in the original deck |

## Open questions

1. The Snellius render carries the SRC asides because the published files
   do. Should upstream keep them, or should the Snellius render drop them
   (`render.asides = []`) and SRC learners get the `build/src` copy instead?
2. Where do SRC learners get the SRC render: a generated branch, a release
   archive, or a `make src` in the class checkout?
3. The SRC aside said three workspaces, and ex4's override had no
   `--ntasks-per-node=2`, so with coursenode4r600 in the partition Slurm may
   put four of the six tasks on that node. The commit "pin two tasks per node
   in the SRC dot product override" fixes both in `src.toml` and regenerates
   the README. Keep it or drop it?
4. `[limits]` encodes today's course rule (two per node). Should the 60-core
   node count as a separate shape, so a profile can offer a "big node"
   variant (for example 16 tasks on coursenode4r600)?
5. Snellius facts marked `# unverified` (mail, default partition, memory per
   node, QCG module name, EESSI init path): worth one check on Snellius before
   upstreaming?
6. Should profiles describe one deployment (the Maastricht course) or a class of
   clusters (any SRC Magic Castle), with the node list filled from `sinfo`?
7. `src.toml` writes the login host as `<manager>`, as the slides do, so the
   course host name stays out of the repository. Should the renderer take the
   real host from an untracked local file or an environment variable, or
   should learners keep reading it from the trainer's setup link?
