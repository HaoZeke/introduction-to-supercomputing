# Cluster-specific values in the course

Inventory for the cluster profiles (see DESIGN.md). Made on 2026-10-28 from
`feat/cluster-profiles` at 389d29a, by grepping job scripts, hands-on
Markdown, READMEs and Org slide sources. The raw grep found 631 matching
lines; they collapse into the 52 values below. Rows 9, 25, 30, 38 and 46
follow the class branch at 389d29a. The SSH pass of 2026-10-28 over the
SRC course cluster updated rows 18, 19, 37 and 50 and added row 53.

Paths are shortened:
FH = course-module-fundamentals-of-hpc, PA = course-module-performance-analysis,
QC = course-module-qcg-pilotjob, FS = course-module-snellius-fs,
HJ = course-module-snellius-hybrid-jobs. `.org` files are under `slides/`.

SRC values were checked live on 2026-10-28 unless marked *unverified*.
Snellius values are what the repo says; *unverified* means nobody checked them
on Snellius for this inventory.

## Partitions and node shapes

| # | Value | Where | Snellius | SRC | Profile key |
|---|---|---|---|---|---|
| 1 | CPU partition in scripts | FH/hands-on.md:190, FH/hands-on/pi.sh:6, python.sh:5, FS/ex1/run.sh:3, FS/README.md:105,166, QC/example_01/array_job.sh:4, example_02/array_job.sh:4, example_03..05/qcg_job.sh:5, example_05/pipeline.sh:5, QC/alternatives/*/*.sh:5, FH .org:2146,2218,2267,2284,2392,2874 | `rome` | `rome` (alias of `cpubase_bycore_b1`, also `thin_course`) | `partitions.cpu` |
| 2 | Default partition | (implicit in HJ scripts, no `-p`) | `rome` *unverified* | `cpubase_bycore_b1` | `slurm.default_partition` |
| 3 | GPU partition | FH/hands-on.md:241 | `gpu_a100` | `gpu` (coursenode3 emulated + coursenode4r600) | `partitions.gpu` |
| 4 | GPU request | FH/hands-on.md:243, PA .org:1843 | `--gpus-per-node=1` | same; add `-w coursenode4r600` for a real GPU | `slurm.gpu_request`, `partitions.real_gpu_node` |
| 5 | GPU model in text | FH/hands-on.md:250 ("one A100"), FH .org:1174,1210, HJ/README.md:36 | A100 40 GB, H100 94 GB | RTX PRO 6000 Blackwell x2, 28 shards; `gpu:emulated:2` on coursenode3 | `system.nodes[].gres` |
| 6 | Partition catalogue | HJ/README.md:33-36, FH .org:982-1222 (rome, fat_rome, himem_4tb, himem_8tb, genoa, fat_genoa, gpu_a100, gpu_h100, staging) | as listed | not present | `system.partition_info` |
| 7 | Cores per node | HJ/README.md:33, QC/hands-on/README.md:43, QC .org:1272 | 128 (rome), 192 (genoa) | 2, 2, 2, 60 | `system.nodes[].cpus` |
| 8 | Node counts | HJ/README.md:29-36, FH .org:922 | 520 rome, 736 genoa, 1,500+ total | 4 | `system.partition_info`, derived `system.node_count` |
| 9 | SRC node summary | FH .org:1730, HJ/README.md:41 | n/a | 4 nodes, 66 CPUs; the slide since 9e7a90f, the README on this branch | `system.nodes` |
| 10 | Minimum allocation | QC/hands-on/README.md:43, QC .org:234,285 | 16 cores, 28 GiB (1/8 rome node) | 1 core, 5559 MB (`DefMemPerCPU`) | `slurm.min_allocation_*`, `slurm.def_mem_per_cpu_mb` |
| 11 | Memory per node | HJ/README.md:34-35,275,345 ("160 GB", `--exclusive`) | 256 GiB rome *unverified*; 1/1.5/4/8 TiB fat/himem | 14713 MB; 333549 MB on coursenode4r600 | `system.nodes[].mem_mb` |
| 12 | Oversubscription | (not in text) | *unverified* | `OverSubscribe=YES:4`, `cons_tres` + `CR_CORE_MEMORY` | `slurm.oversubscribe`, `slurm.select` |

## Job sizes in scripts

| # | Value | Where | Snellius | SRC (course shrink: ≤2 per node) | Profile key |
|---|---|---|---|---|---|
| 13 | HJ ex1/ex3/ex5 `--cpus-per-task` | HJ/hands-on/ex1,ex3,ex5/*.sh:8 | 16 | 1 | `jobs.hybrid.exN` |
| 14 | HJ ex2/ex4 `--ntasks` | HJ/hands-on/ex2,ex4/*.sh:6 | 128 on 1 node | ex2: 2 on 1 node; ex4: 6 on 3 nodes | `jobs.hybrid.ex2`, `.ex4` |
| 15 | HJ README hostname solution | HJ/README.md:185-187, :56 | 2 nodes, 8 tasks, 4 per node | 3 nodes, 6 tasks, 2 per node | `jobs.hybrid.hostname` |
| 16 | HJ results-table columns and sizes | HJ/README.md:267-277, 337-347 | Hyb-16-1 … Hyb-2-128, up to 1e10 | Hyb-2-1, Hyb-6-1, Hyb-1-2, Hyb-3-2, up to 1e8 | `hybrid.table` |
| 17 | HJ sample output local length | HJ/README.md:240,330 | 78125 (128 tasks) | 5000000 / 1666667 | derived from `jobs.hybrid.exN.sample_n` |
| 18 | FH hello.sh | FH/hands-on.md:185,193,219 | 16 cores on 1 rome node | 2 | `jobs.fundamentals.hello`, `fundamentals.hello_why` |
| 19 | FH pi.sh | FH/hands-on/pi.sh:4, FH/hands-on/README.md:16 | 32 | 2 (README override) | `jobs.fundamentals.pi` (pi.sh); README not templated yet |
| 20 | FH slide job scripts | FH .org:2144 (10 tasks), 2216 (4), 2390, 2872 (10) | as written | ≤2 per node | not templated yet |
| 21 | QC example 3 | QC/example_03/qcg_job.sh:2-3, README.md:3 | 2 nodes × 128 tasks | 3 × 2 (README override) | not templated yet |
| 22 | QC examples 4/5, pipeline, alternatives | QC/example_04,05/*.sh:3, alternatives/*/*.sh:3, alternatives/README.md:11-14, hands-on/README.md:43-48 | 16 tasks (FireWorks 1) | 2 | not templated yet |
| 23 | QC arrays | QC/example_01/array_job.sh:6, example_02/array_job.sh:6, hands-on/README.md:45 | `0-11%3`, `0-999%10` | `0-99%10` for ex2 | not templated yet |

## Modules and software

| # | Value | Where | Snellius | SRC | Profile key |
|---|---|---|---|---|---|
| 24 | Stack module | every `module load 2025` (HJ scripts :18 or :17, FH/hands-on.md:176,198, FH/hands-on/*.sh, FS/ex1/run.sh:8, QC example_02, example_05, alternatives, FH .org:2398, QC .org:748, PA .org:1643) | `2025` | `2025` → EESSI 2025.06 | `modules.stack` |
| 25 | Stack on its own line | QC/alternatives/README.md:45,70,100 (split in 6bc1630) | works either way *unverified* | **required**: `module load 2025 X` fails | `modules.stack_on_own_line` |
| 26 | Toolchain | HJ scripts :19 or :18, HJ/README.md:105, FH .org:2399,2208 | `foss/2025a` | same | `modules.toolchain` |
| 27 | Compiler | FH/hands-on.md:177,199, FH/hands-on/pi.sh:9, FS/ex1/run.sh:9 | `GCC/14.2.0` | same | `modules.compiler` |
| 28 | Python | FH/hands-on/python.sh:8, QC examples, alternatives, QC .org:598 | `Python/3.13.1-GCCcore-14.2.0` | same | `modules.python` |
| 29 | QCG-PilotJob | QC/example_03..05/qcg_job.sh:14-16, QC/hands-on/README.md:37-40, QC .org:749,841 | `QCG-PilotJob/0.14.1-GCCcore-14.2.0` *unverified* | site build, same name | `modules.qcg` |
| 30 | QCG names on the SRC slide | FH .org:1729 | n/a | since 9e7a90f the slide points to the course commands page; scripts use the GCCcore-14.2.0 name | `modules.qcg` |
| 31 | Site module path | QC/example_03:13, example_04:13, example_05:15, alternatives/hyperqueue/*.sh:15-16, fireworks/*.sh:16-18 | does not exist | `/cvmfs/course.surf-src.cvmfs/…/amd/zen2/modules/all` | `modules.site_modulepath` |
| 32 | EESSI init path | same 7 scripts, `source /cvmfs/software.eessi.io/versions/2025.06/init/lmod/bash` | EESSI on Snellius *unverified* | works | not templated yet |
| 33 | Workflow tools | QC/alternatives/README.md:25,42,67, alternatives/*/*.sh | no Snakemake, no FireWorks | HyperQueue/0.24.0, snakemake/9.22.0-foss-2025b, FireWorks/2.1.4-gfbf-2025a (site) | not templated yet |
| 34 | SciPy/matplotlib | QC/example_05/README.md:38-39, plot_profile.py:9-10, alternatives/README.md:101 | `SciPy-bundle/2025.06-gfbf-2025a`, `matplotlib/3.10.3-gfbf-2025a` | same | not templated yet |
| 35 | R | (answer key only) | *unverified* | `R/4.5.1-gfbf-2025a`, `R/4.5.2-gfbf-2025b` | `modules.r` |
| 36 | Other EESSI versions | (not in text) | n/a | 2023.06, 2026.06 | `modules.eessi_versions` |

## Paths and file systems

| # | Value | Where | Snellius | SRC | Profile key |
|---|---|---|---|---|---|
| 37 | Home | FH/hands-on.md:47,73-105, FS/README.md:21-27, FH .org:1387 | `/home/<user>` | `/home/<user>` is a symlink: `pwd` after login prints the target, `du -sh ~` prints 512 | `paths.home`, `paths.home_link` |
| 38 | Shared scratch | FS/README.md:13,55-62,84, FS .org:108,147-148, FH .org:1443,2308 | `/scratch-shared/$USER` | none; `/scratch` on shared BeeGFS, `~/scratch` points to `/scratch/$USER` | `paths.scratch_shared`, `paths.scratch_link` |
| 39 | Local scratch / `$TMPDIR` | FS/README.md:67-72,97-143, FH .org:1480,2405-2418, QC example_01,02,04,05, alternatives | `/scratch-local/<user>.<jobid>` → `/gpfs/scratch1/nodespecific/<node>/…` | `/localscratch/$USER.<jobid>.0` | `paths.tmpdir` |
| 40 | Scratch-node | FS/README.md:147-171, FS .org:110, FH .org:1495,1516 | `/scratch-node` with `--constraint=scratch-node` | none | `paths.scratch_node`, `slurm.constraints` |
| 41 | Projects | FS/README.md:14, FS .org:111, FH .org:1528 | `/projects` | `/project`, no `~/projects` | `paths.projects` |
| 42 | Archive | FS/README.md:15, FS .org:112, FH .org:1554 | `/archive` | none | `paths.archive` |
| 43 | Sample user and nodes in output | FS/README.md:6-143 (`scur1448`, `int5`, `int6`, `tcn386`) | real Snellius output | n/a | leave as recorded output |

## Constraints, tools, accounting, mail

| # | Value | Where | Snellius | SRC | Profile key |
|---|---|---|---|---|---|
| 44 | `--constraint=hwperf` | PA .org:468, README.md:30 | needed for counters | absent | `slurm.constraints` |
| 45 | Mail notifications | FH .org:2132,2136 (`--mail-type`, `--mail-user`) | works *unverified* | `MailProg=/bin/mail`, no mail service: accepted, never sent | `slurm.mail` |
| 46 | `myquota` | FH/hands-on.md:23,136, FH .org:1731 | yes | yes; reports the shared home file system | `tools.myquota` |
| 47 | `accinfo`, SBU | FH/hands-on.md:24,142, QC/example_02/README.md:23, example_04/README.md:22-44, example_05/README.md:55, QC .org:583,1425, FH .org:2992 | SBU, 1 per rome core-hour | none; `sacct` `CPUTimeRAW` in core-seconds | `tools.accinfo`, `accounting.unit` |
| 48 | EAR | PA .org:1691,1710-1714,1899 | `eacct -j <jobid>` | none | `tools.ear` |
| 49 | AMD uProf | PA .org:154,1608,1638-1645 | `AMD-uProf/5.1.701` | none | `tools.uprof`, `modules.uprof` |
| 50 | PAPI, perf, likwid | PA .org:1512,1524,1909, README.md:30 | with `hwperf` | PAPI module resolves; `perf stat` counts on a compute node | `tools.papi`, `tools.perf` |

## Network and access

| # | Value | Where | Snellius | SRC | Profile key |
|---|---|---|---|---|---|
| 51 | Interconnect | HJ/README.md:29,41, FH .org:926,1730,1854 | InfiniBand, fat tree | Ethernet | `system.interconnect` |
| 52 | Login host, login nodes, portal | FH/hands-on.md:31,35,37,106,120, FS/README.md:6,80, HJ/README.md:38, FH .org:1704,1728,2894, README.md:42 | `snellius.surf.nl`, `int4`–`int6`, `ondemand.snellius.surf.nl` | `<manager>`; OOD apps shell, files, jupyter, vscode, bc_desktop | `system.login_host`, `system.ondemand_*` |
| 53 | mpifileutils | data-movement deck (not on this branch) | *unverified* | no module | `tools.mpifileutils` |
