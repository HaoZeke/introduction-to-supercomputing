---
title: File systems on a Magic Castle cluster
subtitle: Hands-on data management in high-performance computing
author: Adapted from "Snellius File Systems" by Xavier Álvarez-Farré (SURF)
date: 2026-10-10
---

# Introduction

## Overview of HPC applications

HPC applications are software designed to exploit the power of supercomputers or high-performance clusters to solve complex problems, perform intensive computations, facilitate communications between parallel processes, and manage input/output operations on a high-performance file system.

- **Computations**: extensive numerical operations on a specific region of interest (e.g., mesh elements, particles, or even words in a text document). Scale $O(P)$ for $P$ processors.
- **Communications**: coordination and data exchanges between parallel processes to produce meaningful results. Scale $O(\sqrt{P})$ for $P$ processors.
- **I/O operations**: interactions with the file system to read input data, write output results, and perform intermediate data storage. Usually have no scaling factor.

## Overview of I/O operations

- **Input operations**
  - Initialization data such as geometric grids, genomic sequences, climate simulation data, or large text files: massive files that require a high level of precision and involve parallel input operations.
  - Job parameters that provide instructions for guiding the behavior of the job and coordinating processes are typically stored in small files but require coordination between processes.
- **Output operations**
  - Restart files or checkpoints enable job continuation in the event of an interruption: large files at full precision, written periodically in parallel.
  - Analysis data for visualization, post-processing and in-depth examination: reduced precision or a subset may do; written periodically in parallel.
  - Job monitoring data, typically written by process 0 in a human-readable format such as ASCII.

## Overview of the cluster file systems

HPC applications read and write data with different needs, and HPC systems provide a file system for each. A Magic Castle cluster serves three shared file systems over the network file system (NFS) from its management node, and gives each job space on the node's disk.

| File system | Where | Shared | Size | Backed up | Expiration |
|---|---|---|---|---|---|
| `/home` | NFS on `mgmt1` | Yes | Set at build | No | Cluster lifetime |
| `/scratch` | NFS on `mgmt1` | Yes | Set at build | No | Cluster lifetime |
| `/project` | NFS on `mgmt1` | Group | Set at build | No | Cluster lifetime |
| `/localscratch/<user>.<job>.0` | Node disk | No | Node disk | No | End of job |

Software comes from the European Environment for Scientific Software Installation (EESSI) under `/cvmfs/software.eessi.io` (read-only).

# Hands-on

## Objectives of the hands-on session

1. Navigating file systems: home, project, scratch, node-local scratch
2. File management: create, view, edit, move, rename and copy files across file systems
3. Directory management: create, navigate and delete directories
4. File permissions: check and modify access permissions
5. Disk usage monitoring: storage usage and free space across file systems

## 1. Navigating file systems

- Key commands: `pwd`, `ls`, `cd <path>`
- Tasks: start in the home directory and check it with `pwd`; `cd` to `~/scratch`; list it with `ls`; return home with `cd`.
- Expected outcome: comfortable navigating and exploring directories on the cluster.

## 2. File management

- Key commands: `touch`, `nano` or `vim`, `cat`, `cp <src> <tgt>`, `mv <src> <tgt>`
- Tasks: create a file in your home directory; edit it and view it; copy it to `~/scratch`; rename or move it.
- Expected outcome: create, edit, copy and rename files.

## 3. Directory management

- Key commands: `mkdir`, `cd`, `rmdir`, `ls`
- Tasks: create a directory in your home; enter it; list it; return home; remove it.
- Expected outcome: create, enter and remove directories.

## 4. File permissions

- Key commands: `ls -l`, `chmod`
- Permissions read `rwxrwxrwx` for owner, group, others; r = 4, w = 2, x = 1; `chmod 755` gives the owner rwx and group and others r-x.
- Tasks: check a file's permissions; make it readable for everyone with `chmod 644`; verify with `ls -l`. Try the same on a file in `~/projects/def-sponsor00` and ask a neighbour to read it.

## 5. Disk usage monitoring

- Key commands: `df -h`, `du -sh`
- Tasks: run `df -h /home /scratch /project` to see size and free space; check the size of a directory in your home with `du -sh`; find where you use the most space.
- There is no `myquota`: everyone shares the same volumes, so check `df` before writing large files.
