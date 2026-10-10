# Hands-on file systems on the course cluster

> Rohit Goswami adapted this module from `course-module-snellius-fs` (SURF,
> GPL-3.0) on 2026-10-10. It targets a
> [Magic Castle](https://github.com/ComputeCanada/magic_castle) Slurm cluster
> on SURF cloud resources, with software from the
> [European Environment for Scientific Software Installation (EESSI)](https://www.eessi.io/docs/).
> `CHANGES.md` lists every change from the Snellius version.

Your trainer gives you a guest account such as `user01`, a password,
and the address of the cluster's login node. Open a terminal and log in with
`ssh`. In the examples below the cluster is called `src-eessi`.

```
$ ssh user01@<login address>
[user01@login1 ~]$
```

On the login node, we will identify the different file systems:
1. `/home`
2. `/scratch`
3. `/project`
4. `/localscratch` and `/tmp` on the compute nodes

All three shared file systems are network file system (NFS) exports from the management node
(`mgmt1`). A Magic Castle cluster has no `/archive`.

## Home
The home file system, `/home`, has one directory per user, `/home/<username>`. It is your personal workspace for scripts, configuration files and small inputs. The home directory is private by default. You can change its permissions, but keep them restrictive.

Right after logging in via ssh, the prompt is in your home directory. You can check this with the print working directory command, `pwd`:

```
[user01@login1 ~]$ pwd
/home/user01
```

Snellius has a `myquota` command; Magic Castle does not, and it does not enable NFS quotas by default. Check the size and free space of the file system instead, and how much of it you use:

```
[user01@login1 ~]$ df -h /home
[user01@login1 ~]$ du -sh ~
```

All participants share the same `/home` volume, whose size was set when the cluster was created. **Nothing on the cluster is backed up.** When the trainer removes the cluster with `terraform destroy`, every file system goes with it, so copy anything you need to keep to your own machine with `scp` or `rsync` before the end of the course.

Home sits on the same NFS server as `/scratch` and `/project`, so none of them is faster than the others. The split is about who can see the files and what you agree to keep there.

## Scratch
The scratch file system is for temporary data of running jobs. Every user has a directory `/scratch/<username>`, and `~/scratch` links to it:

```
[user01@login1 ~]$ ls -ld ~/scratch
[user01@login1 ~]$ df -h /scratch
```

Snellius offers three distinct scratch file systems. On Magic Castle there are two kinds:
* Shared: `/scratch`, the same on every node.
* Node-local: `/localscratch` and a private `/tmp` on each compute node, created per job.

### Shared scratch
`/scratch` is visible from the login node and from every compute node. It suits data that more than one job step or node reads.

```
[user01@login1 ~]$ touch /scratch/user01/testfile-scratch.foo
[user01@login1 ~]$ ls /scratch/user01/
testfile-scratch.foo
```

### Node-local scratch
Inside a job, Slurm gives you a private directory on the compute node's own disk, `/localscratch/<username>.<jobid>.0`, and also mounts a private `/tmp` for the job. Other jobs, and the login node, cannot see them. When the job ends, Slurm deletes both.

First, create a file in `/tmp` on the login node:

```
[user01@login1 ~]$ echo "a file on login1" > /tmp/testfile-login1.foo
[user01@login1 ~]$ cat /tmp/testfile-login1.foo
a file on login1
```

Now run a short command on a compute node. The file on `/scratch` is there; the file in the login node's `/tmp` is not.

```
[user01@login1 ~]$ srun -t 5 ls -l /scratch/user01/ /tmp/
```

Next, use the script below to launch a job that lists its node-local directory, creates a file there, and prints the paths.

```
#!/bin/bash
#SBATCH -J files
#SBATCH -t 5

LOCAL=/localscratch/$USER.$SLURM_JOB_ID.0
ls -l $LOCAL
hostname -s > "$LOCAL/testfile.foo"
ls -l $LOCAL
echo $LOCAL
ls -l /tmp
```

Submit it twice with `sbatch` and compare the two `slurm-<jobid>.out` files. Each job prints its own directory name, which contains the job id, and each job starts with an empty directory, even when both land on the same node: node-local scratch is node-specific and job-specific.

Because Slurm removes these directories at the end of each job, node-local files do not pile up and count against anyone. Copy results to `/scratch` or `/home` before your job script ends.

#### Exercise
Modify the script above so the job writes a file to its node-local directory, copies it to `/scratch/$USER`, and prints the real path of both copies.

```
#!/bin/bash
#SBATCH -J localscratch-test
#SBATCH -t 5

LOCAL=/localscratch/$USER.$SLURM_JOB_ID.0
echo "This is a file on node-local scratch" > "$LOCAL/testfile-local.foo"
cp "$LOCAL/testfile-local.foo" /scratch/$USER/
realpath "$LOCAL/testfile-local.foo" /scratch/$USER/testfile-local.foo
```

## Project
Accounts on the cluster belong to the group `def-sponsor00`. Its directory `/project/def-sponsor00` is shared by all members, and `~/projects/def-sponsor00` links to it. Use it for inputs and results the whole group needs.

```
[user01@login1 ~]$ ls -ld ~/projects/def-sponsor00
[user01@login1 ~]$ df -h /project
```

## Software from EESSI
The cluster gets its software from EESSI through CernVM-FS, mounted at `/cvmfs/software.eessi.io`. Logging in sets up the EESSI environment for the version the cluster was built with:

```
[user01@login1 ~]$ echo $EESSI_VERSION
[user01@login1 ~]$ module avail GCC
```

The exercises use these modules. Pick the column that matches `$EESSI_VERSION`:

| Purpose | EESSI 2025.06 | EESSI 2023.06 |
|---|---|---|
| C compiler for `ex1` | `GCC/14.3.0` | `GCC/13.2.0` |
| Parallel gzip | `pigz/2.8-GCCcore-14.3.0` | `pigz/2.8-GCCcore-13.2.0` |
| Zstandard compression | `zstd/1.5.7-GCCcore-14.3.0` | `zstd/1.5.5-GCCcore-13.2.0` |

To use the other EESSI version in a shell, make the EESSI modules visible and load one:

```
[user01@login1 ~]$ module use /cvmfs/software.eessi.io/init/modules
[user01@login1 ~]$ module load EESSI/2023.06
```

`ex1/run.sh` compiles `ex1/print-n.c` with GCC from EESSI and writes arrays of increasing size to your home directory. Submit it with `sbatch run.sh` from the `ex1` directory.

#### Advanced exercise: Creating large file sets and evaluating transfers

##### Objective
- Learn how to generate large numbers of files with random data.
- Compare the efficiency of transferring these files as individual files versus transferring them as an archive between different file systems (e.g., home and scratch).

##### Set-up guide

1. **Create a directory for the test**:
   - Create a directory to store the random files:
     ```bash
     mkdir ~/file_transfer_test
     cd ~/file_transfer_test
     ```

2. **Generate random files**:
   - Use a `for` loop to create 1000 files, each with random data.
   - You can use the `dd` command or `head` with `/dev/urandom` to generate files with random data. Here's an example of creating 1000 files with 1 MB of random data each:
     ```bash
     for i in {1..1000}; do
         head -c 1M </dev/urandom > file_$i.bin
     done
     ```
   - **Explain**: This loop generates 1000 binary files (`file_1.bin`, `file_2.bin`, ..., `file_1000.bin`), each with 1 MB of random data.

3. **Check the size of the directory**:
   - After creating the files, check the total size of the directory:
     ```bash
     du -sh ~/file_transfer_test
     ```
   This gives you an idea of how much data will be transferred.

##### Moving the files between file systems

Now, we'll move these files between different file systems (from **home** to **scratch**, or to node-local scratch inside a job) in two different ways:
1. Moving the individual files.
2. Moving a compressed archive of the files.

1. **Transfer as individual files**:
   - Use `time` to measure how long the transfer takes:
     ```bash
     time cp -r ~/file_transfer_test /scratch/$USER/
     ```

2. **Transfer as an archive**:
   - Archive and compress the directory using `tar` and `gzip`:
     ```bash
     cd ~
     time tar -czf file_transfer_test.tar.gz file_transfer_test
     ```
   - The same with parallel gzip from EESSI (2023.06: `pigz/2.8-GCCcore-13.2.0`):
     ```bash
     module load pigz/2.8-GCCcore-14.3.0
     time tar -I pigz -cf file_transfer_test.tar.gz file_transfer_test
     ```
   - Measure the size of the compressed archive:
     ```bash
     du -sh file_transfer_test.tar.gz
     ```
   - Now, transfer the archive to the **scratch** directory:
     ```bash
     time cp file_transfer_test.tar.gz /scratch/$USER/
     ```

3. **Extract the archive in the scratch directory**:
   - Once the transfer is complete, extract the archive in the scratch directory to restore the files:
     ```bash
     cd /scratch/$USER/
     tar -xzf file_transfer_test.tar.gz
     ```

4. **Repeat on node-local scratch**:
   - Inside an interactive job, copy the archive to node-local disk and unpack it there:
     ```bash
     srun -t 15 --pty bash
     LOCAL=/localscratch/$USER.$SLURM_JOB_ID.0
     time cp /scratch/$USER/file_transfer_test.tar.gz $LOCAL/
     time tar -xzf $LOCAL/file_transfer_test.tar.gz -C $LOCAL
     exit
     ```

##### Evaluate the performance

1. **Compare transfer times**:
   - Review the `time` command outputs from both transfers (individual files vs. archive).
   - Discuss how much time it took to transfer the files as individual files versus as a compressed archive.

2. **Compare data size**:
   - Check the total size of the original directory and the compressed archive. Random data does not compress, so expect the archive to be about as large as the directory; the gain comes from moving one file instead of 1000.

3. **Discuss trade-offs**:
   - **When to use individual file transfers**: If you're working with a small number of files or if they will be used directly without further processing.
   - **When to use archived file transfers**: Bundling many small files into one reduces the number of NFS metadata operations, which dominate the cost of copying small files.

4. **Advanced considerations**:
   - Discuss how these operations scale using larger directories or more participants writing to the same NFS server at once.
   - Introduce the concept of **I/O bottlenecks** in HPC and why proper file management is crucial when working with large data sets.

##### Clean-up

- After the hands-on session, guide the participants to clean up the directories and files to free up space on the shared volumes:
  ```bash
  rm -r ~/file_transfer_test
  rm ~/file_transfer_test.tar.gz
  rm -r /scratch/$USER/file_transfer_test
  rm /scratch/$USER/file_transfer_test.tar.gz
  ```
