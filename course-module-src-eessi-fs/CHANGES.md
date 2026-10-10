# Changes from course-module-snellius-fs

This module is a modified copy of `course-module-snellius-fs` from
[sara-nl/introduction-to-supercomputing](https://github.com/sara-nl/introduction-to-supercomputing),
released under version 3 of the General Public License (GPL), see
`LICENSE` at the repository root. The changes below were made by Rohit Goswami on 2026-10-10.
The module keeps the original's layout: `README.md` for the hands-on,
`ex1/` for the I/O exercise, and `slides/`.

## Target system

| Snellius | Magic Castle on SURF cloud resources with the European Environment for Scientific Software Installation (EESSI) |
|---|---|
| `ssh scur1448@snellius.surf.nl`, course accounts `scurNNNN` | `ssh user01@<login address>`, guest accounts `user01`..`userNN` with a shared password |
| Login nodes `int5`, `int6` | One login node, `login1` |
| Compute node names such as `tcn386.local.snellius.surf.nl` | `node1`, `node2`, `node3`; scripts print `hostname -s` |
| General Parallel File System (GPFS) | Network file system (NFS) exports from the management node `mgmt1` |

## File systems

| Snellius | Magic Castle |
|---|---|
| `/home/<user>`, 200 GiB quota, nightly incremental backup, kept 3 weeks | `/home/<user>` on a shared NFS volume, no per-user quota, no backup |
| `/scratch-shared/<user>`, 8 TiB quota shared with scratch-local, files expire after 6 or 14 days | `/scratch/<user>` (link `~/scratch`), shared NFS volume, no expiry, gone when the cluster is destroyed |
| `/scratch-local` via `$TMPDIR`, GPFS, under `/gpfs/scratch1/nodespecific/<node>/<user>.<jobid>` | `/localscratch/<user>.<jobid>.0` on the node's disk plus a private `/tmp`, both created per job by Slurm and deleted at job end; `$TMPDIR` is not set |
| `/scratch-node` NVMe via `--constraint=scratch-node`, `$TMPDIR` | Removed: no node features; every job gets node-local space |
| `/project`, on demand | `/project/def-sponsor00` (link `~/projects/def-sponsor00`), shared by all guest accounts |
| `/archive`, tape, backed up | Removed: no archive on the cluster |
| `myquota` | `df -h` and `du -sh`; Magic Castle leaves NFS quotas off by default |
| `ls -ld /gpfs/scratch1/nodespecific/*/<user>.*` to find leftover files | Removed: the Slurm epilog deletes node-local directories |

## Hands-on text (`README.md`)

- The `int6` versus `int5` comparison of `$TMPDIR` now compares the login node's `/tmp` with a job on a compute node, because there is one login node.
- The `$TMPDIR` job script now uses `LOCAL=/localscratch/$USER.$SLURM_JOB_ID.0`; the sample outputs with Snellius node and job names are replaced by instructions to compare the two job outputs.
- The scratch-node exercise now writes to node-local scratch and copies the file to `/scratch/$USER`.
- New sections "Project" and "Software from EESSI".
- The advanced exercise replaces `/path/to/scratch/` with `/scratch/$USER/`, adds a `pigz` variant from EESSI, and adds a node-local scratch step.
- Correction not specific to Snellius: data from `/dev/urandom` does not compress, so the text no longer says the archive saves disk space; it explains the gain as fewer file operations.
- Added a modification notice at the top, as GPL-3.0 section 5(a) requires.

## Job scripts

| Snellius | Magic Castle |
|---|---|
| `#SBATCH -p thin_course`, `#SBATCH -p rome` | No `-p`: the default partition is `cpubase_bycore_b1` |
| Default memory per core of the Snellius partitions | `#SBATCH --mem=2G` in `ex1/run.sh`; Magic Castle's default is 256 MB per CPU |
| `#SBATCH --constraint=scratch-node` | Removed |
| `ex1/run.sh`: `iend=10`, `nmax=10**10` (up to 80 GB per array) | `iend=9`, `nmax=10**8` (up to 800 MB), sized for small cloud nodes and a shared NFS home |
| No accounting changes needed in this module; Snellius bills in System Billing Units (SBU), as SURF names them | No billing units; cost is the cloud allocation for the cluster's VMs |

## Software modules

| Snellius | EESSI 2025.06 | EESSI 2023.06 |
|---|---|---|
| `module load 2023` | none: set up at login (`/cvmfs/software.eessi.io/versions/<version>/init/Magic_Castle/bash`) | same |
| `module load GCC/12.3.0` | `GCC/14.3.0` | `GCC/13.2.0` |
| (new) | `pigz/2.8-GCCcore-14.3.0` | `pigz/2.8-GCCcore-13.2.0` |
| (new) | `zstd/1.5.7-GCCcore-14.3.0` | `zstd/1.5.5-GCCcore-13.2.0` |

Checked on 2026-10-10 against `/cvmfs/software.eessi.io` for the `generic`,
`amd/zen2`, `amd/zen3`, `amd/zen4`, `intel/haswell`, `intel/skylake_avx512`,
`intel/icelake` and `intel/sapphirerapids` x86_64 targets. `print-n.c`
compiles and runs with both GCC modules. Switching versions with
`module use /cvmfs/software.eessi.io/init/modules` and
`module load EESSI/2023.06` works from a 2025.06 shell.

## Slides

`slides/snellius-fs.pdf` is not copied. `slides/src-eessi-fs.md` is a pandoc
source with the same nine slides. Slide 3 (file system overview and table) is
rewritten for Magic Castle, slides 5, 6, 8 and 9 use `~/scratch`,
`~/projects/def-sponsor00` and `df -h` instead of Snellius paths and
`myquota`. Building the PDF needs pandoc with a LaTeX engine.

## Not yet checked on a live cluster

The Magic Castle facts above come from puppet-magic_castle 16.0.3
(`site/profile/manifests/slurm.pp`, `templates/slurm/slurm.conf.epp`,
`files/accounts/account_functions.sh`, `data/common.yaml`) and the
spank-cc-tmpfs_mounts source. Run the hands-on once on the course cluster
before teaching it.
