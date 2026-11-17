# Hands-on {{system.display_name}} file systems

Open a terminal to access to {{system.display_name}} via `ssh`.

```
$ ssh scur1448@{{system.login_host}}
Last login: Wed Nov 8 18:33:29 2023
[scur1448@{{system.login_node_alt}} ~]$
```

On the login node, we will identify the different file systems:
1. `/home`
2. `{{paths.scratch_root}}`
3. `{{paths.projects}}`
4. `{{paths.archive}}`

{{#asides}}
{{fs.aside_note}}

{{/asides}}
{{^asides}}
{{fs.self_note}}

{{/asides}}
## Home
The home file system, often denoted as `/home`, is the storage space dedicated to individual user accounts on {{system.display_name}}. It serves as a personal workspace where users can store their important files, configuration files, scripts, and other data. **Each user on {{system.display_name}} has their own dedicated home directory** within the `/home` file system, which is found at `/home/<username>`. The home directory is usually private and can only be accessed by the user who owns it. Other users typically don't have access to your home directory. Although you can change its access permissions, you should be very restrictive in using this capability.

Right after logging into {{system.display_name}} via ssh, the prompt will be located at your home. You can check this via the path to the working directory command, `pwd`, as follows:

```
[scur1448@{{system.login_node_alt}} ~]$ pwd
/home/scur1448
```

The home file system often has disk space quotas associated with it. Users are allocated a specific amount of storage space, and it's essential to be mindful of your usage to avoid exceeding your quota. The number of individual files, or inodes, is also limited. You can check your quota and current usage with the `{{commands.quota}}` command.

```
[scur1448@{{system.login_node_alt}} ~]$ {{commands.quota}}
scur1448@home4|GiB:quota=200.00,limit=210.00,usage=0.0000%|Inodes:quota=1000000,limit=1200000,usage=0.0008%
```

The home directory is typically designed for **long-term storage of essential files** and data. It's not the ideal location for temporary or large files that you're actively working on. Files stored in the home directory are often **backed up regularly to prevent data loss** in case of hardware failures or accidental file deletion. SURF supplies a versioned **incremental backup service** for your home directory that is run overnight. Files that have been backed up are retained in the backup repository for **three weeks** after they have been deleted from the file system. We can restore files and/or directories when you accidentally remove them or overwrite them with the wrong contents.

While the home file system is suitable for long-term storage, it's not optimized for high-performance I/O or large data processing tasks. For such operations, other file systems like `/scratch` or `{{paths.projects}}` may be more suitable.

## Scratch
The scratch file systems are intended as fast temporary storage that can be used while running a job and can be accessed by all users with a valid account on the system. A user's default scratch space capacity quota is 8 TiB, which is counted over all data usage of scratch-local and scratch-shared of the user. Again, you can check your quota and current usage with the `{{commands.quota}}` command.

```
[scur1448@{{system.login_node_alt}} ~]$ {{commands.quota}}
scur1448@wstor_scratch1|TiB:quota=8.00,limit=10.00,usage=0.0038%|Inodes:quota=3000000,limit=4000000,usage=0.0014%
```

{{system.display_name}} offers three distinct scratch file systems to meet various storage and performance requirements.
* Shared. 
* Local.
* Node.

### Scratch-shared
{{^paths.scratch_user?}}
The scratch-shared file system, denoted as `{{paths.scratch_root}}`, is a shared workspace accessible from all compute nodes on {{system.display_name}}. It is designed for temporary and high-performance storage, making it suitable for parallel and distributed computing tasks.

You can create your own directory using your `<username>`, or any other filename.
{{/paths.scratch_user?}}
{{#paths.scratch_user?}}
This cluster has no `{{paths.scratch_root}}`. Its shared scratch is `{{paths.scratch_shared}}` on {{paths.shared_fs}}, and your directory `{{paths.scratch_user}}` already exists, so the commands below use it.
{{/paths.scratch_user?}}

```
{{^paths.scratch_user?}}
[scur1448@{{system.login_node}} ~]$ mkdir {{paths.scratch_root}}/scur1448
[scur1448@{{system.login_node}} ~]$ touch {{paths.scratch_root}}/scur1448/testfile-scratch-shared.foo
[scur1448@{{system.login_node}} ~]$ ls {{paths.scratch_root}}/scur1448/
{{/paths.scratch_user?}}
{{#paths.scratch_user?}}
[scur1448@{{system.login_node}} ~]$ touch {{paths.scratch_user}}/testfile-scratch-shared.foo
[scur1448@{{system.login_node}} ~]$ ls {{paths.scratch_user}}/
{{/paths.scratch_user?}}
testfile-scratch-shared.foo
```

### Scratch-local
The scratch-local file system is dedicated to individual compute nodes on {{system.display_name}}. While it sits on the same GPFS infrastructure as the scratch-shared system, it is uniquely configured for each compute node upon the initiation of a job. You can access it via the environment variable `$TMPDIR`. For example, follow the steps below to create a test file on login node `{{system.login_node}}` (if you did not land on `{{system.login_node}}`, you can either switch or adapt the next steps to your specific login node).

```
[scur1448@{{system.login_node}} ~]$ touch $TMPDIR/testfile-local-{{system.login_node}}.foo
[scur1448@{{system.login_node}} ~]$ echo "a file in {{system.login_node}}" > $TMPDIR/testfile-local-{{system.login_node}}.foo
[scur1448@{{system.login_node}} ~]$ cd $TMPDIR
[scur1448@{{system.login_node}} scur1448]$ ll
total 1
-rw-r----- 1 scur1448 scur1448 15 Nov  8 23:33 testfile-local-{{system.login_node}}.foo
[scur1448@{{system.login_node}} scur1448]$ cat testfile-local-{{system.login_node}}.foo 
a file in {{system.login_node}}
```

Now, let's switch to the login node `{{system.login_node_alt}}` by using `ssh {{system.login_node_alt}}`. First, verify whether the file in the scratch-shared system is still present.

```
[scur1448@{{system.login_node}} scur1448]$ ssh {{system.login_node_alt}}
{{^paths.scratch_user?}}
[scur1448@{{system.login_node_alt}} ~]$ ll {{paths.scratch_root}}/scur1448/
{{/paths.scratch_user?}}
{{#paths.scratch_user?}}
[scur1448@{{system.login_node_alt}} ~]$ ll {{paths.scratch_user}}/
{{/paths.scratch_user?}}
total 0
-rw-r----- 1 scur1448 scur1448 0 Nov  8 23:13 testfile-scratch-shared.foo
```

Next, confirm that the file in the scratch-local system is absent.

```
[scur1448@{{system.login_node_alt}} ~]$ ls $TMPDIR
[scur1448@{{system.login_node_alt}} ~]$ 
```

> [!NOTE]
> On an SRC cluster, `$TMPDIR` in a job is `{{course_cluster.paths.tmpdir}}` on the node's own disk, and the cluster deletes it when the job ends. The cluster has one login node, so compare the login node's `/tmp` with a job's `$TMPDIR` instead of comparing `{{system.login_node_alt}}` with `{{system.login_node}}`.

Next, use the script below to launch a job that lists the contents of `$TMPDIR`, creates a file, and prints the path and real path to `$TMPDIR`.

```
#!/bin/bash
#SBATCH -J files
#SBATCH -t 5
#SBATCH -p {{partitions.cpu}}

hostname
ls -l $TMPDIR
touch "$TMPDIR/testfile.foo"
ls -l $TMPDIR
echo $TMPDIR
realpath $TMPDIR
```

We executed the job twice and provided the outputs below. Despite both jobs being allocated to the same node, it's shown that the scratch-local directory is not only node-specific but also job-specific.

```
[scur1448@{{system.login_node_alt}} ~]$ cat slurm-4401218.out
tcn386.local.{{system.login_host}}
total 0
total 0
-rw-r----- 1 scur1448 scur1448 0 Nov  9 00:25 testfile.foo
{{paths.scratch_local}}/scur1448.4401218
/gpfs/scratch1/nodespecific/tcn386/scur1448.4401218
```

```
[scur1448@{{system.login_node_alt}} ~]$ cat slurm-4401219.out
tcn386.local.{{system.login_host}}
total 0
total 0
-rw-r----- 1 scur1448 scur1448 0 Nov  9 00:25 testfile.foo
{{paths.scratch_local}}/scur1448.4401219
/gpfs/scratch1/nodespecific/tcn386/scur1448.4401219
```

In this configuration, you might occasionally lose track of files generated by your jobs in the scratch-node file system, potentially leading to the consumption of your allocated quota. To address this, you can use the following commands to locate all your files on the scratch file system:

```
[scur1448@{{system.login_node_alt}} ~]$ ls -ld /gpfs/scratch1/nodespecific/*/scur1448.*
drwxr-xr-x 2 scur1448 scur1448 4096 Nov  9 00:19 /gpfs/scratch1/nodespecific/tcn386/scur1448.4401213
drwxr-xr-x 2 scur1448 scur1448 4096 Nov  9 00:25 /gpfs/scratch1/nodespecific/tcn386/scur1448.4401218
drwxr-xr-x 2 scur1448 scur1448 4096 Nov  9 00:25 /gpfs/scratch1/nodespecific/tcn386/scur1448.4401219
```

### Scratch-node
The scratch-node behavior is technically similar to scratch-local. For each assigned node, a user-specific partition is created and mounted under `{{paths.scratch_node}}`. The environment variable `$TMPDIR` points to the user-specific directory within `{{paths.scratch_node}}`, which should be used within your job. However, there are some differences that are worth noting:
1. Scratch-node operates on NVMe-based storage and is physically located on the node itself.
2. When a user's job is completed, their respective file system mounted under `{{paths.scratch_node}}` will be automatically removed. Therefore, it's essential to copy your data from `$TMPDIR` to a more permanent location at the end of your job script.
3. There are no quotas imposed on `{{paths.scratch_node}}`, and no backup policy is in place. Users should exercise caution in data management.

Please be aware that when requesting a shared node, you will only receive a portion of the local NVMe disk, such as 25%, 50%, or 75%, depending on the requested job resources.

Scratch-node is available on all fat nodes and on a subset of the `{{partitions.cpu}}`, `{{partitions.cpu_alt}}` and GPU nodes. To secure a node with the scratch-node file system, you may use the `--constraint={{slurm.scratch_constraint}}` flag in your job configuration.

{{#paths.scratch_node?}}
> [!NOTE]
> Scratch-node and `--constraint={{slurm.scratch_constraint}}` exist only on {{system.display_name}}. On an SRC cluster, `$TMPDIR` already sits on the node's own disk, so drop the constraint and write to `$TMPDIR` in the exercise.
{{/paths.scratch_node?}}
{{^paths.scratch_node?}}
> [!NOTE]
> This cluster has no scratch-node file system and no `scratch-node` constraint. `$TMPDIR` already sits on the node's own disk, so the script below leaves the constraint out and writes to `$TMPDIR`.
{{/paths.scratch_node?}}

#### Exercise
Modify the script above to launch a job that creates a file on scratch-node and displays the file's real path.

```
#!/bin/bash
#SBATCH -J scratch-node-test
#SBATCH -t 5
#SBATCH -p {{partitions.cpu}}
{{#paths.scratch_node?}}
#SBATCH --constraint={{slurm.scratch_constraint}}
{{/paths.scratch_node?}}

touch "$TMPDIR/testfile-scratch-node.foo"
echo "This is a file on scratch-node" > "$TMPDIR/testfile-scratch-node.foo"
realpath "$TMPDIR/testfile-scratch-node.foo"
```

#### Advanced exercise: Creating large file sets and evaluating transfers

> On an SRC cluster, `/home` and `/scratch` use the configured shared storage; the Maastricht course uses BeeGFS. Check `df -h` before generating data. Run this exercise with 100 files instead of 1000 (`{1..100}`), use a job's `$TMPDIR` as the second file system, and do the clean-up at the end. `ex1/run.sh` defaults to 10^6 and 10^7 values in the job's `$TMPDIR`, falling back to home outside a job. To compare home storage, submit `wdir="$HOME" sbatch run.sh` from the `ex1` directory. The environment variables `ibeg`, `iend` (exclusive), and `nmax` control the range; increasing them requires enough memory for the array and enough disk space for the output. Never set `wdir` to a login node's `$TMPDIR` for a compute job.

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

Now, we'll move these files between different file systems (e.g., from **home** to **scratch** or **project**) in two different ways: 
1. Moving the individual files.
2. Moving a compressed archive of the files.

1. **Transfer as individual files**:
   - First, move the files individually:
     ```bash
     cp -r ~/file_transfer_test /path/to/scratch/
     ```
   - Use `time` to measure how long the transfer takes:
     ```bash
     time cp -r ~/file_transfer_test /path/to/scratch/
     ```

2. **Transfer as an archive**:
   - Archive and compress the directory using `tar` and `gzip`:
     ```bash
     tar -C ~ -czf ~/file_transfer_test.tar.gz file_transfer_test
     ```
   - Measure the size of the compressed archive:
     ```bash
     du -sh ~/file_transfer_test.tar.gz
     ```
   - Now, transfer the archive to the **scratch** directory:
     ```bash
     time cp ~/file_transfer_test.tar.gz /path/to/scratch/
     ```

3. **Extract the archive in the scratch directory**:
   - Once the transfer is complete, extract the archive in the scratch directory to restore the files:
     ```bash
     cd /path/to/scratch/
     tar -xzf file_transfer_test.tar.gz
     ```

##### Evaluate the performance

1. **Compare transfer times**:
   - Review the `time` command outputs from both transfers (individual files vs. archive).
   - Discuss how much time it took to transfer the files as individual files versus as a compressed archive.

2. **Compare data size**:
   - Check the total size of the original directory and the archive. The files contain random data, which gzip cannot compress, so the archive has about the same size.

3. **Discuss trade-offs**:
   - **When to use individual file transfers**: If you're working with a small number of files or if they will be used directly without further processing.
   - **When to use archived file transfers**: Packing many small files into one archive reduces transfer time, because the copy needs fewer file operations. Compression saves disk space only for data that compresses, such as text.

4. **Advanced considerations**:
   - Discuss how these operations scale using larger directories or more complex file systems.
   - Introduce the concept of **I/O bottlenecks** in HPC and why proper file management is crucial when working with large data sets.

##### Clean-up

- After the hands-on session, guide the participants to clean up the directories and files to free up space on the system:
  ```bash
  rm -r ~/file_transfer_test
  rm ~/file_transfer_test.tar.gz
  rm -r /path/to/scratch/file_transfer_test
  rm /path/to/scratch/file_transfer_test.tar.gz
