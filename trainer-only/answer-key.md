
# Table of Contents

1.  [How the answers were chosen](#org141fbb1)
2.  [The course cluster](#orgbc34f57)
3.  [Fundamentals, the login shell](#orgc4abd11)
    1.  [Questions 1 to 4, identity](#orgdc5d1f3)
    2.  [The environment listing](#org4c9fcbe)
    3.  [A variable that dies with the shell](#org3b1de45)
    4.  [Last login](#orge512281)
    5.  [Quota](#org7ad267c)
    6.  [Compute budget](#org04ba9cf)
4.  [Fundamentals, compiling and the first jobs](#orgbc56522)
    1.  [OpenMP hello](#org2b6fccf)
    2.  [sacct and seff](#org13397f6)
    3.  [First GPU job](#orgf692958)
    4.  [Slide job, the one-minute limit](#org275edd6)
    5.  [Slide job, srun and mpirun](#org2f9cf29)
    6.  [Slide job, a dependency](#org239ed60)
    7.  [An R template](#orgdb9c907)
    8.  [python.sh](#org1f90daf)
    9.  [pi.sh and the thread count](#org688d1fc)
5.  [File systems, Snellius slides](#org85b1d32)
    1.  [1. Move between filesystems](#org0e6a8d2)
    2.  [2. Create, copy, rename](#org2d97714)
    3.  [3. Directories](#org110cd03)
    4.  [4. Permissions](#org5eb2433)
    5.  [5. Disk use](#org7052d35)
6.  [File systems, the Snellius hands-on](#org79fc98d)
    1.  [Home, shared scratch, and a login node&rsquo;s TMPDIR](#orgdff94b0)
    2.  [A job&rsquo;s own scratch directory](#orgef8fcd1)
    3.  [Leftover scratch files](#orgac1a5df)
    4.  [Scratch-node](#org7d59aad)
    5.  [A thousand small files](#org98875cc)
    6.  [print-n](#org740834f)
7.  [Moving data](#org9909928)
    1.  [Twenty thousand files, three copies, one checksum](#orga780893)
    2.  [Resume an interrupted copy](#orgcd0d9e0)
    3.  [Stage into the job](#orge479669)
8.  [File systems on a Magic Castle](#orgdaa97a2)
    1.  [Navigate, manage files, manage directories](#org04a18cf)
    2.  [Permissions and disk use](#orgb0defde)
    3.  [Node-local scratch](#orgd98e9ac)
    4.  [EESSI modules, pigz and zstd](#org7d7a7f6)
9.  [Hybrid jobs](#org2301217)
    1.  [Load the compiler inside the job](#orgc04e2da)
    2.  [Hostname across nodes](#orga3da709)
    3.  [Sequential axpy](#org3ce8312)
    4.  [Hybrid axpy](#org4ce6707)
    5.  [Sequential and hybrid dot product](#org7a7ead2)
    6.  [Matrix multiplication, the open exercise](#org1f1a18e)
10. [Performance analysis](#org9f8d84d)
    1.  [Strong scaling, weak scaling, efficiency](#org12e2740)
    2.  [Flop counts](#orga8cb58a)
    3.  [Roofline arithmetic intensity](#org4ff7ce3)
    4.  [Hardware counters and massif](#orge10110a)
    5.  [Energy](#org87219b5)
11. [Job arrays and QCG-PilotJob](#orge097e2a)
    1.  [Example 1, a twelve-task array](#orgf093b4d)
    2.  [Example 2, averages with an array](#org668d7a6)
    3.  [Example 3, five hundred and twelve short tasks](#orgfac168f)
    4.  [Example 4, why the versions change](#org3427341)
    5.  [Example 5, the sleep pipeline](#orgb66b79b)
12. [HyperQueue, Snakemake and FireWorks](#org5613698)
    1.  [HyperQueue](#org266f7ae)
    2.  [Snakemake](#orgd1112dd)
    3.  [FireWorks](#orgab975c6)
    4.  [Questions](#orgbd45620)
13. [What was executed](#orgff7b9f7)

This directory is for trainers. It is the answer key for every exercise
in the course: the hands-on pages, the slide tasks, the data-movement
deck, and the Magic Castle filesystem module. Learners do not need it.

Each exercise records the commands, the shape of a correct result, the
reason that result is correct, and whether that result was produced on
the machine that prepared this key. `run` means the commands were
executed here and the invariant was checked. `not-run` means the
commands need Snellius, a tool this machine does not have, or a run
that was deliberately left at the published measurement. Timings always
belong to the machine that produced them. The numbers that do not
depend on the machine are the ones to mark.


<a id="org141fbb1"></a>

# How the answers were chosen

The commands below are the ones in this tree, which already contains
the corrections to the 2025 software stack, the Snellius facts, the
QCG aggregation scripts, the Org sources of the decks, and the
HyperQueue, Snakemake and FireWorks versions of examples 4 and 5.

Two further sets of exercises are included from branches that are not
in this tree:

-   The data-movement hands-on (pack, checksum, resume an interrupted
    `rsync`, stage into `$TMPDIR`).
-   The filesystem module written for a Magic Castle cluster with EESSI,
    including its `print-n` job and the `pigz` / `zstd` transfer.

Where the live SURF Research Cloud course cluster (recorded 2026-10-28)
differs from a plain Magic Castle, both are named. The live cluster is
the one trainers should follow during the course.


<a id="orgbc34f57"></a>

# The course cluster

On the SURF Research Cloud Magic Castle course cluster with EESSI, the
following substitutions apply to every exercise that uses them. Later
sections repeat a substitution only when the exercise fails without it.

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Snellius</th>
<th scope="col" class="org-left">Course cluster</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left"><code>ssh &lt;user&gt;@snellius.surf.nl</code>, login nodes <code>int4</code>, <code>int5</code>, <code>int6</code></td>
<td class="org-left">the manager address the trainer gives; one login node</td>
</tr>


<tr>
<td class="org-left"><code>module load 2025</code> then the tool, and both may share a line</td>
<td class="org-left"><code>module load 2025</code> on its own line, then the tool. One line fails</td>
</tr>


<tr>
<td class="org-left"><code>module load 2025</code> is the SURF 2025 stack</td>
<td class="org-left"><code>module load 2025</code> is EESSI 2025.06</td>
</tr>


<tr>
<td class="org-left"><code>GCC/14.2.0</code>, <code>foss/2025a</code>, <code>Python/3.13.1-GCCcore-14.2.0</code></td>
<td class="org-left">the same names resolve</td>
</tr>


<tr>
<td class="org-left"><code>QCG-PilotJob/0.14.1-gfbf-2024a</code> after <code>module load 2024</code></td>
<td class="org-left">site build <code>QCG-PilotJob/0.14.1-GCCcore-14.2.0</code> after <code>module load 2025</code></td>
</tr>


<tr>
<td class="org-left">partition <code>rome</code></td>
<td class="org-left">default <code>cpubase_bycore_b1</code>; <code>rome</code> and <code>thin_course</code> are aliases of it</td>
</tr>


<tr>
<td class="org-left"><code>gpu_a100</code></td>
<td class="org-left">partition <code>gpu</code>. Real cards are on <code>coursenode4r600</code>; add <code>--nodelist=coursenode4r600</code> to skip the emulated GPU node</td>
</tr>


<tr>
<td class="org-left"><code>--constraint=scratch-node</code>, <code>--constraint=hwperf</code></td>
<td class="org-left">neither feature exists. Drop the constraint</td>
</tr>


<tr>
<td class="org-left"><code>/scratch-shared</code>, <code>/scratch-local</code>, <code>/scratch-node</code>, <code>/archive</code>, <code>/gpfs</code></td>
<td class="org-left">absent. Shared scratch is <code>/scratch/$USER</code> (<code>~/scratch</code> already exists). Project is <code>/project</code>. <code>$TMPDIR</code> in a job is <code>/localscratch/$USER.$SLURM_JOB_ID.0</code></td>
</tr>


<tr>
<td class="org-left"><code>myquota</code>, <code>accinfo</code>, SBU</td>
<td class="org-left"><code>myquota</code> reports the shared home filesystem. There is no <code>accinfo</code>. Accounting is core-hours: <code>CPUTimeRAW / 3600</code></td>
</tr>


<tr>
<td class="org-left"><code>#SBATCH --mail-type</code> and <code>--mail-user</code></td>
<td class="org-left">accepted, and no mail is sent</td>
</tr>


<tr>
<td class="org-left">AMD uProf, EAR, <code>eacct</code>, mpiFileUtils</td>
<td class="org-left">absent. PAPI and <code>perf</code> are present. <code>seff</code> is present</td>
</tr>


<tr>
<td class="org-left">128 and 256 core columns, <code>N=10^9</code> and <code>N=10^10</code></td>
<td class="org-left">drop them. Nodes coursenode1&#x2013;3 have 2 CPUs; coursenode4r600 has 60</td>
</tr>
</tbody>
</table>

A plain Magic Castle, without that course profile, is stricter:

-   There is no `rome` alias. Omit `-p rome`.
-   `myquota` is absent. Use `df -h` and `du -sh ~/`.
-   `$SLURM_TMPDIR` is `/localscratch/$USER.$SLURM_JOB_ID.0`. Slurm sets
    `$TMPDIR` to a private `/tmp`, which is a different directory.
-   Home, scratch and project are NFS from the management node. The
    project link is `~/projects/def-sponsor00`.
-   The EESSI compiler after `module load 2025` is `GCC/14.3.0` (2025.06)
    or `GCC/13.2.0` (2023.06), and `pigz` and `zstd` come from those
    stacks. QCG-PilotJob is not in EESSI; only a site module provides it.
-   Guest accounts are `user01` onwards.

Home on the course cluster is a symlink. `du -sh ~` measures the link.
`du -sh ~/` measures the files.


<a id="orgc4abd11"></a>

# Fundamentals, the login shell


<a id="orgdc5d1f3"></a>

## Questions 1 to 4, identity

Status: run

Commands:

    whoami
    echo "$USER"
    pwd
    echo "$PWD"
    echo "$HOME"
    hostname
    echo "$HOSTNAME"

Output shape: four facts, each command agreeing with the matching
variable. `pwd` and `$PWD` are the same directory. On Snellius that
directory is `/home/<username>` and the hostname looks like
`int6.local.snellius.surf.nl`. Append them to `~/<username>.dat` with
`>>`.

Reasoning: the shell expands `$USER`, `$PWD`, `$HOME` and `$HOSTNAME`
from the login environment. A script that writes `$HOME` works for every
account; a script that writes `/home/johnd` works for one account.

Here: user `ubuntu`, home `/home/ubuntu`, host `cursor`. `pwd` and
`$PWD` matched.

On the course cluster the home path is still `/home/$USER`, and the
hostname is the manager, not `int6`.


<a id="org4c9fcbe"></a>

## The environment listing

Status: run

Command: `env`. The listing contains `SHELL`, `USER`, `HOME` and `PATH`,
then many more names. Record `$PWD`, `$HOME` and `$HOSTNAME` in the
`.dat` file rather than the whole listing.


<a id="org3b1de45"></a>

## A variable that dies with the shell

Status: run

    NEWVAR="Hello_123"
    echo "$NEWVAR"
    bash -c 'echo "child:${NEWVAR-unset}"'
    export NEWVAR
    bash -c 'echo "exported:${NEWVAR}"'

Output shape: the current shell prints `Hello_123`. A new process prints
an empty value until `export`. After a real logout and a new SSH login
the variable is gone either way.

Reasoning: an assignment lives in that shell. A child receives only the
exported environment. A new login reads `~/.bashrc` and
`~/.bash_profile`, not the previous shell. Putting `export NEWVAR`&#x2026;=
in `~/.bashrc` is what makes it survive a login.

Here the unexported child printed `unset` and the exported child printed
`Hello_123`.


<a id="orge512281"></a>

## Last login

Status: run

Command: `last -n 1 -R $USER`. The flag order matters: `last -n -R 1`
is the broken form.

Output shape on Snellius, one line:

    <username>  pts/5        <host>  Tue Oct 28 20:12   still logged in

`last` reads `wtmp`. Here `wtmp` has no login record, so the command
printed only `wtmp begins ...`. That is a successful run of the command
on a machine that has never recorded an SSH login.


<a id="org7ad267c"></a>

## Quota

Status: not-run

Command on Snellius: `myquota`. Shape: a home block (about 200 GiB, a
limit near 210 GiB, an inode quota) and a scratch block (about 8 TiB).
The percentages belong to that account.

On the course cluster `myquota` does run, and it reports the shared
home filesystem, which is also where scratch and project live. It does
not report a private 200 GiB home and a private 8 TiB scratch.

On a plain Magic Castle there is no `myquota`. Use:

    df -h /home /scratch /project
    du -sh ~/

This machine has no `myquota`. `df -h` shows one disk for `/`, `/tmp`
and `/home`.


<a id="org04ba9cf"></a>

## Compute budget

Status: not-run

Command on Snellius: `accinfo`. It prints the account&rsquo;s budget and
usage in SBUs. The numbers are per account.

On the course cluster, and on a plain Magic Castle, `accinfo` is
absent. Skip the question. Billing is the collaboration wallet, and
the unit a job report can show is the core-hour from `sacct`.


<a id="orgbc56522"></a>

# Fundamentals, compiling and the first jobs


<a id="org2b6fccf"></a>

## OpenMP hello

Status: run

    mkdir -p "$HOME/hello" && cd "$HOME/hello"
    # hello.c as in the hands-on, then:
    module purge
    module load 2025
    module load GCC/14.2.0
    gcc -O2 -fopenmp hello.c -o hello
    sbatch hello.sh
    squeue -u "$USER"
    cat hello-<jobid>.out

`hello.sh` asks for 16 cores on `rome`, sets
`OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK`, and runs `./hello`.

Output shape: one line per thread,

    Hello from thread <k> of <T>

`<T>` equals the cores the job received. The lines are not sorted.
`squeue` shows `PD` while the job waits and `R` while it runs, then the
job leaves the queue.

Reasoning: the `parallel` region runs one thread per core. The runtime
does not print in thread order.

Here, with `--cpus-per-task=4` on an 8-core node, four lines appeared,
threads 0&#x2013;3, unsorted. A request for 16 cores stays pending on this
node and on a 2-core course node.

On the course cluster submit `sbatch --cpus-per-task=2 hello.sh`. Keep
the two `module load` lines separate. `rome` is an alias there; on a
plain Magic Castle drop `-p rome` or the job is rejected.


<a id="org13397f6"></a>

## sacct and seff

Status: not-run

    sacct -j <jobid> --format=JobID,JobName,Partition,AllocCPUS,State,Elapsed
    seff <jobid>

Output shape: `sacct` prints the job id, the name, the partition, the
allocated CPUs, `COMPLETED` (or `TIMEOUT` / `FAILED`), and the elapsed
time. `seff` prints CPU efficiency (CPU time used, divided by cores
times elapsed time) and memory efficiency. A short kernel that also
compiles looks inefficient; compare configurations with each other.

This machine was built with accounting storage turned off, so `sacct`
answers that accounting is disabled, and `seff` is not installed. On
the course cluster both commands work. Read `CPUTimeRAW` as
core-seconds and divide by 3600 for core-hours. There is no SBU column
to interpret.


<a id="orgf692958"></a>

## First GPU job

Status: not-run

`gpu.sh` requests `--partition=gpu_a100` and `--gpus-per-node=1`, then
runs `nvidia-smi`.

Output shape: the `nvidia-smi` table for the one GPU the job received,
including the GPU name and the memory line.

This machine has no GPU and no `gpu_a100` partition. `sbatch` rejected
the script with an invalid generic-resource specification.

On the course cluster the partition is `gpu`, not `gpu_a100`.
`coursenode3` advertises an emulated GPU. For a real card:

    sbatch --partition=gpu --gpus-per-node=1 --nodelist=coursenode4r600 gpu.sh


<a id="org275edd6"></a>

## Slide job, the one-minute limit

Status: run

`job.sh` from the first job slide: `--nodes=1 --ntasks=10
--time=00:01:00 --partition=rome`, then `whoami`, `srun hostname`,
`sleep 120`, `date`, `echo DONE`.

    sbatch job.sh
    squeue -u "$USER"
    scontrol show job <jobid>
    ls

Output shape: `whoami` prints the account once. `srun hostname` prints
one line per task, so ten lines when ten tasks fit. The job is then
killed. The output file contains a time-limit message and does not
contain `DONE`. `scontrol show job` shows `TIMEOUT` and the end time.
The new file is `slurm-<jobid>.out` (or the name set by `--output`).

Reasoning: the wall time is one minute and the script sleeps two
minutes. Slurm cancels the job at the limit, which is the error the
slide asks for. The repair is `--time=00:03:00`, or a shorter sleep.
`whoami` is one process. `srun` starts one process per task.

Here the script was submitted with `--ntasks=2` (this node has 8
CPUs; the slide&rsquo;s 10 is fine on a `rome` node). The output showed the
username, two hostname lines, and `CANCELLED ... DUE TO TIME LIMIT`.
`DONE` was absent.

On the course cluster use `--ntasks=2` on the 2-core nodes. Mail lines
`#SBATCH --mail-type=BEGIN,END` and `#SBATCH --mail-user=<address>` are
valid Slurm and do send mail on Snellius. On the course cluster the
lines are accepted and no mail is sent. The mail step was not run here.


<a id="org2f9cf29"></a>

## Slide job, srun and mpirun

Status: run

`mpi_job.sh`: `--ntasks=4`, then `srun hostname`. Repeat with
`--ntasks=8`. Then delete `srun`. Then, after two module lines, replace
the launch with `mpirun hostname`.

Output shape:

-   `srun hostname` prints the node name once per task. Four tasks give
    four lines; eight tasks give eight. On one node every line is the
    same name.
-   Without `srun`, `hostname` runs once, in the batch shell, so one line.
-   `mpirun hostname` after `module load 2025` and `module load foss/2025a`
    prints one line per rank. The rank count follows the allocation.

Reasoning: `sbatch` reserves the cores and runs the script once.
`srun` and `mpirun` are what fan a command out across those cores.

Here, four tasks: `srun` printed `cursor` four times. The same script
with the bare `hostname` printed it once. `mpirun -np 4 hostname` after
the two module lines printed it four times. Eight tasks and a second
node were not run: this machine has one node and 8 CPUs.

On the course cluster the two-node part of the hostname exercise is
`sbatch --nodes=3 --ntasks=6 --ntasks-per-node=2`. Expect up to three
distinct short hostnames, two lines each. Load `2025` and `foss/2025a`
on separate lines before `mpirun`.


<a id="org239ed60"></a>

## Slide job, a dependency

Status: run

    sbatch first-job.sh
    sbatch --dependency=afterok:<jobid> second-job.sh
    squeue -u "$USER"

`first-job.sh` sleeps 30 seconds and prints `First job finished.`
`second-job.sh` prints `Second job started after first job!`

Output shape: while the first job runs, the second sits in `PD` with
reason `Dependency`. After the first reaches `COMPLETED`, the second
runs and prints its line. If the first job fails or times out,
`afterok` never releases the second, and it stays pending until it is
cancelled.

Here the second job was `PD (Dependency)` and then completed with that
sentence. The sleep in the check was 15 seconds; the slide&rsquo;s 30 seconds
behaves the same way inside a one-minute limit.


<a id="orgdb9c907"></a>

## An R template

Status: not-run

Fill the skeleton from the modules slide:

    #!/bin/bash
    #SBATCH --job-name="r_test"
    #SBATCH --nodes=1
    #SBATCH --ntasks=1
    #SBATCH --time=00:05:00
    #SBATCH --partition=rome
    module purge
    module load 2025
    module load R/4.5.1-gfbf-2025a
    echo "START"
    Rscript -e "rnorm(1)"
    echo "DONE"

Output shape: `START`, one normal random number (a different value on
every run), `DONE`. `module avail R` is how a learner finds the name.

The slide asks for `--ntasks=10`. `Rscript` is one process, so one task
is the honest request; ten tasks only reserve idle cores. `rnorm(1)`
has no fixed value to memorise.

R is not installed here. On the course cluster the two module lines
stay separate, and both `R/4.5.1-gfbf-2025a` and `R/4.5.2-gfbf-2025b`
resolve. On a plain Magic Castle take the R module `module avail` lists
under EESSI, and drop `-p rome` if that partition does not exist.


<a id="org1f90daf"></a>

## python.sh

Status: run

`sbatch python.sh` from `course-module-fundamentals-of-hpc/hands-on`.
The script loads `2025` and `Python/3.13.1-GCCcore-14.2.0` on separate
lines and sums `range(1000000)`.

Output shape:

    Python on <hostname>
    sum: 499999500000

Reasoning: the sum of `0 .. 999999` is `n(n-1)/2` with `n = 1000000`.

The slide asks where a scratch copy would go. On Snellius, copy inputs
from `/scratch-shared/$USER` into `$TMPDIR` at the start of the script
and copy outputs back before the script exits. On the course cluster
the shared copy lives in `/scratch/$USER` (the `~/scratch` link is
already there) and `$TMPDIR` is the node-local directory the job
deletes at the end.


<a id="org688d1fc"></a>

## pi.sh and the thread count

Status: run

`./compilepi` on the login node, then `sbatch pi.sh`. `pi.sh` loops
`OMP_NUM_THREADS` over 1, 2, 4, 8 and 32 and stops once the count would
pass `$SLURM_CPUS_PER_TASK`.

Output shape: for every thread count,

    pi = 3.141592654

followed by a time that falls as the thread count rises, until the
machine runs out of useful cores. The value of pi does not change.

Reasoning: the midpoint rule on `1/sqrt(1-x^2)` over `[-1, 1)` with
`10^8` steps is stable at the printed digits. The work is a parallel
loop with a reduction, so more threads shorten the loop until they
exceed the cores or the problem becomes too small to split.

Here, inside the job (4 CPUs requested): 0.103 s, 0.052 s, 0.026 s for
1, 2 and 4 threads. A direct run with 8 threads stayed at 0.026 s, so
eight threads did not beat four on this 8-core machine for this loop.
The 32-thread step is skipped whenever the job has fewer than 32 CPUs.

On the course cluster request `--cpus-per-task=2`. The loop then prints
the 1-thread and 2-thread lines.


<a id="org85b1d32"></a>

# File systems, Snellius slides

These five tasks are the hands-on in the filesystem deck. They use
`/scratch-shared`, which the course cluster does not have. Do the same
steps under `/scratch/$USER` (see the Magic Castle section).


<a id="org0e6a8d2"></a>

## 1. Move between filesystems

Status: run

    cd
    pwd
    mkdir -p /scratch-shared/$USER
    cd /scratch-shared/$USER
    pwd
    ls
    cd

Output shape: the first `pwd` is `/home/$USER`. The second is
`/scratch-shared/$USER`. `ls` is empty the first time.

On the course cluster `mkdir -p /scratch-shared/$USER` fails because
that tree does not exist. `cd ~/scratch` is the replacement, and the
directory is already there, so the `mkdir` is unnecessary. `pwd` then
shows `/scratch/$USER`. A plain Magic Castle uses the same `~/scratch`
link. This machine has neither path; the same commands were run inside
a private directory and the `pwd` / `cd` / `ls` sequence behaved as
described.


<a id="org2d97714"></a>

## 2. Create, copy, rename

Status: run

    cd
    touch notes.txt
    printf 'hello\n' > notes.txt
    cat notes.txt
    cp notes.txt /scratch-shared/$USER/notes.txt
    mv /scratch-shared/$USER/notes.txt /scratch-shared/$USER/notes-renamed.txt

Output shape: `cat` prints `hello`. After `mv`, `ls` in the scratch
directory shows `notes-renamed.txt` and does not show `notes.txt`.


<a id="org110cd03"></a>

## 3. Directories

Status: run

    cd
    mkdir demo-dir
    cd demo-dir
    ls
    cd
    rmdir demo-dir

Output shape: `ls` inside the new directory is empty. `rmdir` succeeds
only while the directory is empty; a directory that still holds a file
makes `rmdir` print an error and leave it in place. `rm -r` is the
command for a directory that is not empty.


<a id="org5eb2433"></a>

## 4. Permissions

Status: run

    ls -l notes.txt
    chmod 644 notes.txt
    ls -l notes.txt

Output shape: the mode field becomes `-rw-r--r--`. That is owner read
and write, group read, others read. The leading dash means a regular
file. `644` is `rw-` (6) for the owner and `r--` (4) for group and
others.

Here `ls -l` printed `-rw-r--r--` after `chmod 644`.


<a id="org7052d35"></a>

## 5. Disk use

Status: run

    df -h /home /scratch-shared /projects
    du -sh "$HOME"
    du -sh ~/

Output shape: `df -h` prints a size, a used amount and an available
amount for each mount. `du -sh` prints one total for that directory.

On Snellius the three paths are different filesystems, and home carries
a quota that `myquota` shows. On the course cluster those three paths
are one shared filesystem, `/scratch-shared` and `/projects` do not
exist, and the command is `df -h /home /scratch /project`. Because home
is a symlink, `du -sh ~` prints the size of the link and `du -sh ~/`
prints the size of the files.


<a id="org79fc98d"></a>

# File systems, the Snellius hands-on


<a id="orgdff94b0"></a>

## Home, shared scratch, and a login node&rsquo;s TMPDIR

Status: run

    pwd                                  # /home/$USER on Snellius
    mkdir -p /scratch-shared/$USER
    touch /scratch-shared/$USER/testfile-scratch-shared.foo
    printf 'a file on this login\n' > "$TMPDIR/testfile-local.foo"
    ls -l "$TMPDIR"

Output shape: `pwd` is the home directory. The shared file is visible
from every login node. The `$TMPDIR` file is visible only on the login
node that created it; `ssh` to another login node and `ls $TMPDIR`
there does not list it. A fresh file created with `touch` is empty
(size 0) and typically mode `-rw-r-----`.

Reasoning: `/scratch-shared` is one GPFS tree mounted everywhere.
`$TMPDIR` on a login node is that node&rsquo;s own temporary directory.

The course cluster has one login node, so there is no `int5` versus
`int6` comparison. Compare the login node&rsquo;s `/tmp` with the `$TMPDIR`
printed by a job. There is no `/scratch-shared`; the shared file goes
in `~/scratch`.


<a id="orgef8fcd1"></a>

## A job&rsquo;s own scratch directory

Status: run

    #!/bin/bash
    #SBATCH -J files
    #SBATCH -t 5
    #SBATCH -p rome
    hostname
    ls -l "$TMPDIR"
    touch "$TMPDIR/testfile.foo"
    ls -l "$TMPDIR"
    echo "$TMPDIR"
    realpath "$TMPDIR"

Submit it twice.

Output shape, per job: the compute-node hostname, an empty listing, a
listing of one empty `testfile.foo`, then two paths. On Snellius the
first path is `/scratch-local/$USER.<jobid>` and `realpath` rewrites it
to `/gpfs/scratch1/nodespecific/<node>/$USER.<jobid>`. The two jobs get
different directories even when they land on the same node.

Here each job printed `cursor`, created the file, and reported a
distinct `/tmp/slurm-<jobid>`. `realpath` stayed on the same disk,
because this machine has no GPFS.

On the course cluster drop `-p rome` only if you are on a plain Magic
Castle; the course cluster accepts it as an alias. `$TMPDIR` prints
`/localscratch/$USER.$SLURM_JOB_ID.0`. The `/gpfs/...` lookup does not
exist, and the epilog deletes the directory, so there is nothing to
hunt for afterwards. On a plain Magic Castle print `$SLURM_TMPDIR` as
well: that is the `/localscratch` path, while `$TMPDIR` is a private
`/tmp`.


<a id="orgac1a5df"></a>

## Leftover scratch files

Status: not-run

    ls -ld /gpfs/scratch1/nodespecific/*/$USER.*

Output shape: one line per leftover job directory, each a directory
owned by the user.

This path exists only on Snellius. The command was not run. On the
course cluster the job epilog removes the node-local directory. Shared
scratch is `ls ~/scratch`.


<a id="org7d59aad"></a>

## Scratch-node

Status: not-run

    #!/bin/bash
    #SBATCH -J scratch-node-test
    #SBATCH -t 5
    #SBATCH -p rome
    #SBATCH --constraint=scratch-node
    touch "$TMPDIR/testfile-scratch-node.foo"
    echo "This is a file on scratch-node" > "$TMPDIR/testfile-scratch-node.foo"
    realpath "$TMPDIR/testfile-scratch-node.foo"

Output shape on Snellius: one path under `/scratch-node`, on the node
that carries the `scratch-node` feature (every fat node, and some
`rome`, `genoa` and GPU nodes). The directory disappears when the job
ends, so a result that must survive has to be copied out before the
script exits. The feature is absent from a shared node that did not
receive the constraint, and the job then waits.

Here `sbatch` rejected the script immediately: this Slurm has no node
features, so the message is `Invalid feature specification`.

On the course cluster the constraint does not exist and would leave the
job pending forever. Delete the `#SBATCH --constraint` line. `$TMPDIR`
is already the node disk. Copy anything worth keeping to `~/scratch`
before the script ends.


<a id="org98875cc"></a>

## A thousand small files

Status: run

The hands-on builds 1000 files of 1 MB from `/dev/urandom`, times
`cp -r`, then times a gzipped tar.

Output shape: `du -sh` on the directory reports about 1000M. `time`
prints `real`, `user` and `sys`; `real` is the number to write down.
The gzipped archive is about the same size as the directory. The
archive copy has a smaller `real` time than the copy of the individual
files, once the file count is large enough for metadata to matter.

Reasoning: bytes from `/dev/urandom` do not compress, so gzip does not
save disk space. The archive wins because the copy creates one file
instead of a thousand. Thirty files of 256 KiB on this disk finished in
about 4 ms either way, which is too little to see the effect. Twenty
thousand tiny files, in the data-movement exercise, did show it.

On the course cluster `/home` and `/scratch` share one filesystem, so a
copy between them does not cross a network link. Use 100 files, take
the job&rsquo;s `$TMPDIR` as the second filesystem, and delete the tree at
the end. Check `df -h` before generating a gigabyte.


<a id="org740834f"></a>

## print-n

Status: run

From `course-module-snellius-fs/ex1`:

    sbatch run.sh
    # or, to write on home:
    wdir="$HOME" sbatch run.sh
    # range: ibeg, iend (iend is exclusive), nmax
    ibeg=3 iend=5 nmax=100000 wdir="$HOME" sbatch run.sh

The script compiles `print-n.c` and, for `n = 10^k` with `k` from
`ibeg` inclusive to `iend` exclusive, writes `n` numbers as text and as
binary.

Output shape for `n = 1000`:

    1000 random numbers as ascii
    File size [MB]: 0.009000
    Printing 1000 elements

and the same for the binary file with `0.008000`. A non-positive `n`
prints `<n> must be a positive integer'` (the source keeps that stray
quote) and exits non-zero. `n` above `nmax` prints `You are attempting
to print too much data` and exits 1.

Reasoning: the text format is `%.6lf\n`, which is 9 bytes per value, so
`1000 * 9 / 10^6 = 0.009` MB. The binary format is one `double`, 8
bytes, so `0.008` MB. The megabyte figure is the size divided by
`10^6`, matching the transfer-rate arithmetic.

Here `ibeg=3 iend=4 nmax=100000` produced the 0.009000 MB line and
`Printing 1000 elements`.

On the course cluster the script runs as it is: `rome` is an alias and
`module load 2025` loads EESSI. The default `wdir` is the job&rsquo;s
`$TMPDIR`. Asking for `iend` much past 7 needs more memory than a
2-core node has (the array is `n` doubles) and more disk than the node
scratch has. The Magic Castle copy of this exercise uses `--mem=2G`,
`iend=9` and `nmax=1e8` on a larger node; keep the course-cluster run
inside `nmax=1e5` unless the job lands on `coursenode4r600`.


<a id="org9909928"></a>

# Moving data

This is the hands-on from the data-movement deck. mpiFileUtils
(`dwalk`, `dcp`, `dsync`, `drm`, `dtar`) is not in EESSI 2023.06 or
2025.06, and the course cluster has no such module. The hands-on uses
`tar`, `sha256sum` and `rsync`, which are enough.


<a id="orga780893"></a>

## Twenty thousand files, three copies, one checksum

Status: run

    mkdir -p src out
    yes data | head -n 20000 | split -l 1 -a 5 -d - src/f
    ls src | wc -l
    { time cp -r src out/by-cp; }
    tar --sort=name -cf src.tar src
    { time cp src.tar out/; }
    { time rsync -a src/ out/by-rsync/; }
    sha256sum src.tar > src.tar.sha256
    cp src.tar.sha256 out/
    ( cd out && sha256sum -c src.tar.sha256 )

Output shape: `wc -l` prints `20000`. Each `time` prints `real`, `user`
and `sys`. The tar copy is one file and is the fast one. `cp -r` and
`rsync -a` each create 20000 files; `rsync` is the slower of those two
because it compares metadata. The last line is `src.tar: OK`.

Here, on ext4: `cp -r` 0.368 s, the tar copy 0.016 s, `rsync -a`
0.702 s, and `sha256sum -c` reported `src.tar: OK`.

On the course cluster do this under `~/scratch`, not under
`/scratch-shared`. The archive still does not shrink if you gzip it:
the payload is the word `data` repeated, which is small, and a random
payload does not shrink at all. The lesson is the file count.


<a id="orgcd0d9e0"></a>

## Resume an interrupted copy

Status: run

    dd if=/dev/zero of=big.bin bs=1M count=48
    mkdir -p part
    timeout 2 rsync -a --partial --bwlimit=2000 big.bin part/ || true
    ls -l big.bin part/big.bin
    rsync -a --partial big.bin part/
    cmp big.bin part/big.bin && echo cmp-ok

Output shape: `big.bin` is 50331648 bytes (48 MiB). After the timed-out
copy, `part/big.bin` is shorter. `rsync` exits non-zero when `timeout`
kills it; that non-zero status is the interruption, not a broken
command. The second `rsync` brings the sizes level, and `cmp` prints
nothing and exits 0.

Here the interrupted file was 4128768 bytes of 50331648, `cmp` exited
0, and the sizes matched afterwards. `--bwlimit=2000` is what makes two
seconds enough; without it the copy finishes before `timeout` fires.


<a id="orge479669"></a>

## Stage into the job

Status: not-run

`stage.slurm` requests `rome` and `--constraint=scratch-node`, copies
`/scratch-shared/$USER/src/` into `$TMPDIR/src/`, then copies it back to
`/scratch-shared/$USER/out/`.

Output shape: `stage-<jobid>.out` is empty of errors, and
`/scratch-shared/$USER/out/` holds the same tree afterwards. The
node-local copy is gone once the job ends.

The constraint was rejected on this machine (`Invalid feature
specification`), so the script was not run.

On the course cluster delete `--constraint=scratch-node` and replace
both `/scratch-shared/$USER` paths with `/scratch/$USER`. `$TMPDIR` is
already `/localscratch/$USER.$SLURM_JOB_ID.0`, and the epilog deletes
it, which is why the copy back has to happen inside the script.


<a id="orgdaa97a2"></a>

# File systems on a Magic Castle

Use this section on the course cluster and on a plain Magic Castle. The
five tasks are the Snellius slide tasks with the paths replaced.


<a id="org04a18cf"></a>

## Navigate, manage files, manage directories

Status: run

    cd && pwd                 # /home/$USER
    cd ~/scratch && pwd && ls
    cd
    touch notes.txt && printf 'hello\n' > notes.txt && cat notes.txt
    cp notes.txt ~/scratch/notes.txt
    mv ~/scratch/notes.txt ~/scratch/notes-renamed.txt
    mkdir "$HOME/demo-dir" && cd "$HOME/demo-dir" && ls && cd && rmdir "$HOME/demo-dir"

Output shape: `pwd` at home is `/home/$USER`. `pwd` in scratch is
`/scratch/$USER`. `cat` prints `hello`. `ls` after `mv` shows the new
name. `rmdir` removes only an empty directory.

On a plain Magic Castle the project directory is
`~/projects/def-sponsor00`, shared by every guest account. `chmod 644`
on a file there lets another guest read it. The course cluster has
`/project` and no `~/projects` link. This machine has no `~/scratch`;
the same sequence was run in a private directory.


<a id="orgb0defde"></a>

## Permissions and disk use

Status: run

`chmod 644` produces `-rw-r--r--`, as in the Snellius task.

    df -h /home /scratch /project
    du -sh ~/

There is no per-user quota on a plain Magic Castle, so `df` is the
check before a large write. On the course cluster `myquota` also
answers, for the one shared filesystem, and `du -sh ~/` is the command
that counts files (home is a symlink).


<a id="orgd98e9ac"></a>

## Node-local scratch

Status: run

On a plain Magic Castle the job script is:

    #!/bin/bash
    #SBATCH -J files
    #SBATCH -t 5
    hostname -s
    LOCAL=${SLURM_TMPDIR:-/localscratch/$USER.$SLURM_JOB_ID.0}
    ls -l "$LOCAL"
    touch "$LOCAL/testfile.foo"
    ls -l "$LOCAL"
    echo "SLURM_TMPDIR=$LOCAL"
    echo "TMPDIR=$TMPDIR"

Submit it twice.

Output shape: two different directories, each containing the job id,
each empty before the `touch`, even when both jobs share a node.
`$TMPDIR` and `$SLURM_TMPDIR` differ: the first is a private `/tmp`,
the second is `/localscratch/$USER.<jobid>.0`.

The localscratch exercise copies the file out before the job ends:

    LOCAL=${SLURM_TMPDIR:-/localscratch/$USER.$SLURM_JOB_ID.0}
    echo "node local" > "$LOCAL/testfile-local.foo"
    mkdir -p /scratch/$USER
    cp "$LOCAL/testfile-local.foo" /scratch/$USER/

Output shape: after the job, `cat /scratch/$USER/testfile-local.foo`
prints `node local`, and the `/localscratch` path is already gone.

On the course cluster `$TMPDIR` itself is the `/localscratch` path, so
the plain-Magic-Castle distinction between the two variables does not
apply. Writing to `$TMPDIR` and copying to `~/scratch` is the whole
exercise. Here the job&rsquo;s `$TMPDIR` was `/tmp/slurm-<jobid>`, a different
directory per job, on one hostname.


<a id="org7d7a7f6"></a>

## EESSI modules, pigz and zstd

Status: run

On a plain Magic Castle:

    module purge
    module load 2025
    module load GCC/14.3.0
    module load pigz/2.8-GCCcore-14.3.0
    time tar -I pigz -cf file_transfer_test.tar.gz file_transfer_test
    module load zstd
    time tar -I zstd -cf file_transfer_test.tar.zst file_transfer_test

The 2023.06 stack uses `GCC/13.2.0` and
`pigz/2.8-GCCcore-13.2.0`.

Output shape: both archives are about the size of the raw directory
when the files came from `/dev/urandom`. `time` reports a smaller
`real` for the single archive copy than for `cp -r` of many files.

Here `pigz` and `zstd` were run on random bytes: the archives matched
the raw size (about 7.6 MB against 7864320 raw bytes). The course
cluster&rsquo;s `module load 2025` resolves `GCC/14.2.0` rather than
`GCC/14.3.0`; use the name `module avail` prints. mpiFileUtils stays
unavailable on both.


<a id="org2301217"></a>

# Hybrid jobs

Invariants, for every configuration:

-   axpy: `y` starts at 2, `x` at 1, `a = 2`, and the kernel repeats 100
    times, so `y[0] = 2 + 100 * 2 * 1 = 202`, printed as `202.000000`.
    The local length is `N` divided by the number of MPI ranks, with the
    remainder on the first ranks. `N = 10000000` and 128 ranks give local
    length `78125`.
-   dot: `x[i] = sin(i)`, `y[i] = 0.5 * cos(i)`, summed over 100
    repetitions. `N = 10^6` prints `10.1628`. `N = 10^7` prints `12.3778`.
    Later digits may move with the order of the reduction. The printed
    digits should match the sequential run.
-   matmul: `A` is filled with 1, `B` with 2, so `Cij = 2 * n` and the
    checksum is `2 * n^3`. `n = 40` gives `128000`, `n = 100` gives
    `2000000`, `n = 500` gives `250000000`.

Times in the README (0.96 s, 0.009 s, 1.22 s, 0.040 s) are one Snellius
run. Any time is acceptable. Efficiency from `seff` is low on a short
kernel because compilation and startup are inside the job; compare
columns, do not treat one percentage as a verdict.

On the course cluster the table columns that fit are Sequential,
Hyb-2-1, Hyb-6-1, Hyb-1-2 and Hyb-3-2. Drop every 128-core and 256-core
column, and drop `N = 10^9` and `N = 10^10` (they need more memory than
`DefMemPerCPU` of 5559 MB times two cores). Commands:

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Exercise</th>
<th scope="col" class="org-left">Course-cluster submission</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">axpy sequential</td>
<td class="org-left"><code>sbatch --cpus-per-task=1 submit-axpy.sh 10000000</code></td>
</tr>


<tr>
<td class="org-left">axpy hybrid</td>
<td class="org-left"><code>sbatch --ntasks=2 submit-axpy-hybrid.sh 10000000</code></td>
</tr>


<tr>
<td class="org-left">dot sequential</td>
<td class="org-left"><code>sbatch --cpus-per-task=1 submit-dot.sh 10000000</code></td>
</tr>


<tr>
<td class="org-left">dot hybrid</td>
<td class="org-left"><code>sbatch --nodes=3 --ntasks=6 --ntasks-per-node=2 submit-dot-hybrid.sh 30000000</code></td>
</tr>


<tr>
<td class="org-left">matmul</td>
<td class="org-left"><code>sbatch --cpus-per-task=1 submit-matmul.sh 500</code></td>
</tr>


<tr>
<td class="org-left">hostname</td>
<td class="org-left"><code>sbatch --nodes=3 --ntasks=6 --ntasks-per-node=2</code></td>
</tr>
</tbody>
</table>

Hyb-6-1 and Hyb-3-2 need the three 2-core nodes:
`sbatch --nodes=3 --ntasks=6 --ntasks-per-node=2 --cpus-per-task=1` and
`sbatch --nodes=3 --ntasks=3 --ntasks-per-node=1 --cpus-per-task=2`.
With more than one OpenMP thread, set `OMP_PLACES=cores` and
`OMP_PROC_BIND=close`, and launch with `srun --cpu-bind=cores`.


<a id="orgc04e2da"></a>

## Load the compiler inside the job

Status: run

`load_modules.sh` loads `2025` and `foss/2025a` on separate lines, runs
`module list` and `mpicc -v`.

Output shape: `module list` shows `2025` and `foss/2025a`. `mpicc -v`
prints the GCC that foss built against, including `gcc version` and the
configure line. A login-node `module load` does not appear in the job,
because the job starts from a clean environment when the script loads
its own modules. That is why the slide says to keep the `module load`
lines inside the script.

Here the job completed and `mpicc -v` printed GCC 13.3.0. That version
is this machine&rsquo;s stand-in compiler: the `module` command accepted the
names and left the system compiler in place. On Snellius and on the
course cluster the same script prints the foss 2025a compiler.


<a id="orga3da709"></a>

## Hostname across nodes

Status: run

The sample solution is `--nodes=2 --ntasks=8 --ntasks-per-node=4` and
`srun hostname`.

Output shape: eight lines, four copies of one node name and four copies
of the other. A single `--nodes=1` run prints one name, repeated once
per task. `--ntasks-per-node` is what forces the even split; without it
Slurm may pack tasks onto one node.

Here one node and four tasks printed one name, four times. The
two-node split was not run.

On the course cluster use `--nodes=3 --ntasks=6 --ntasks-per-node=2` and
expect three names, twice each. The interconnect is Ethernet, so a
multi-node split is a placement check, not an InfiniBand check.


<a id="org3ce8312"></a>

## Sequential axpy

Status: run

`sbatch submit-axpy.sh 10000000` from `hands-on/ex1`.

    Length of the arrays: 10000000
    y[0] = 202.000000
    Time taken for axpy execution: <seconds>

Here `N = 10^6` under Slurm printed `y[0] = 202.000000` in 0.048 s.
The formula is independent of `N` as long as `N >` 1=.


<a id="org4ce6707"></a>

## Hybrid axpy

Status: run

`sbatch submit-axpy-hybrid.sh 10000000` uses the script default, 128
tasks, one thread each.

    Global length of the arrays: 10000000
    Local length of the arrays: 78125
    y[0] = 202.000000
    Time taken for axpy execution: <seconds>

The published `srun` line was submitted here and the binary aborted in
`MPI_Init`. The Open MPI on this machine is not built with Slurm&rsquo;s
process manager, so `srun` cannot start it. The same binary under
`mpirun -np 2` printed local length `5000000` for `N = 10^7` and local
length `500000` for `N = 10^6`, with `y[0] = 202.000000` both times
(0.267 s and 0.028 s). Mark the kernel as run and the `srun` launch as
a property of this MPI build.

On Snellius `srun` is the right launcher and 128 tasks give local
length 78125. On the course cluster stay at `--ntasks=2` (local length
`N/2`) or the three-node forms in the table above. `seff` and `sacct`
work there; they do not work on this machine.


<a id="org7a7ead2"></a>

## Sequential and hybrid dot product

Status: run

`sbatch submit-dot.sh 10000000` prints:

    Length of the arrays: 10000000
    Dot product result: 12.3778
    Time taken for dot product execution: <seconds>

The hybrid script at 128 tasks prints the same result, global length
`10000000` and local length `78125`.

Here the sequential binary at `N = 10^6` printed `10.1628` (0.084 s)
and at `N = 10^7` printed `12.3778`. `mpirun -np 2` at `N = 10^7`
printed `12.3778` with local length `5000000`. `mpirun -np 4` at
`N = 10^6` printed `10.1628` with local length `250000`. The `srun`
submission failed in `MPI_Init` for the same reason as axpy.

Filling the whole timing table was not run. The empty cells are the
learner&rsquo;s measurements. The result column is the invariant.


<a id="org1f1a18e"></a>

## Matrix multiplication, the open exercise

Status: run

`sbatch submit-matmul.sh 40` (the script&rsquo;s example size; the
course-cluster override uses 500).

    <n>
    checksum <2*n^3>
    <seconds>

The checksum is printed with `%.17g`. For `n = 40` that is `128000`.

The open exercise is to parallelise `ex5/matmul.c`. A correct parallel
version keeps the checksum. Shared memory is an OpenMP `parallel for`
on the outer loop with a reduction only if the checksum is accumulated
there; the matrix update itself has no loop-carried dependence. A
distributed version splits the rows of `A` and of `C` and replicates
`B`, or shifts blocks of `B`. Either way rank 0 prints `2 * n^3`.

Here `n = 40` under Slurm printed checksum `128000` in 0.003 s. No
parallel version was written, and `n = 500` was not timed. The checksum
identity `2 * n^3` was checked by hand for `n = 100` and `n = 500`.


<a id="org9f8d84d"></a>

# Performance analysis

The deck is mostly definitions. The exercises are the scaling
arithmetic, the flop counts, the roofline example, the hardware-counter
job, the memory tool, and the energy job.


<a id="org12e2740"></a>

## Strong scaling, weak scaling, efficiency

Status: run

With `s + p = 1`:

-   Amdahl (strong scaling, fixed work): speedup = `1 / (s + p/N)`.
-   Gustafson (weak scaling, work grows with `N`): speedup = `s + p*N`.
-   Efficiency: `T_sequential / (N * T_parallel)`, which is the speedup
    divided by `N`. Ideal strong-scaling speedup is `N`.

At `N = 16`:

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-right" />

<col  class="org-right" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Parallel share</th>
<th scope="col" class="org-right">Amdahl</th>
<th scope="col" class="org-right">Gustafson</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">50% (<code>s = 0.5</code>)</td>
<td class="org-right">1.8824</td>
<td class="org-right">8.50</td>
</tr>


<tr>
<td class="org-left">95% (<code>s = 0.05</code>)</td>
<td class="org-right">9.1429</td>
<td class="org-right">15.25</td>
</tr>
</tbody>
</table>

Reasoning: the serial fraction runs once no matter how many cores you
add, so a code that is half serial never reaches a speedup of 2. Weak
scaling lets the parallel part grow, so the same code reaches 8.5.

Computed here from the formulas. No scaling job was required for these
slides.


<a id="orga8cb58a"></a>

## Flop counts

Status: run

-   axpy, one pass: `2N` flops (one multiply and one add per element).
    The course kernel repeats it 100 times, so `200 N` flops.
-   Dense matrix-matrix product, textbook triple loop: `2 n^3` flops.
-   FFT of length `N`: `O(N log N)`.

These are the counts to place a kernel on the roofline. They were
checked against the axpy and matmul sources.


<a id="org4ff7ce3"></a>

## Roofline arithmetic intensity

Status: run

The worked example on the slide:

    Throughput  6.7257 GFLOP/s
    Bandwidth   2.6767 GB/s

Arithmetic intensity is throughput divided by bandwidth:

    6.7257 / 2.6767 = 2.5127 FLOP/byte

The slide rounds that to 2.5 FLOP/byte. A point left of the ridge is
bandwidth-bound: raise the intensity or the achieved bandwidth. A point
under the flat roof is compute-bound: the bandwidth is already enough.

The measurement command on Snellius is:

    module purge
    module load 2025
    module load AMD-uProf/5.1.701
    AMDuProfPcm roofline -X -o res.csv -- <prog> <args>

That command was not run. It needs a Snellius node, `--constraint=hwperf`
and `--exclusive`. The course cluster has no uProf and no `hwperf`
feature. Measure with PAPI or `perf stat` there, and compute the same
ratio from the counters you did collect.


<a id="orge10110a"></a>

## Hardware counters and massif

Status: not-run

A counter job on Snellius needs `#SBATCH --constraint=hwperf` and
`#SBATCH --exclusive`. Without them the counters stay unavailable and
the tool reports zeros or refuses to start.

Memory shape, when `valgrind` is installed:

    valgrind --tool=massif ./program
    ms_print massif.out.*

`ms_print` draws a time axis and a peak useful-heap snapshot. The peak
is the number to compare across versions of the program.

Neither tool is on this machine, and the course cluster has no
`hwperf` constraint. PAPI and `perf` are the replacements for the
counter exercise. `valgrind` can be installed as a user tool; it is not
part of the course stack.


<a id="org87219b5"></a>

## Energy

Status: not-run

On Snellius, add to the job:

    #SBATCH --ear=on
    #SBATCH --ear-policy=monitoring
    export EARL_REPORT_LOOPS=1

Then `eacct -j <jobid>`. The table has one row per job step: job step,
user, application, energy in joules, time in seconds, power in watts,
and the frequency columns. The slide&rsquo;s illustration is job
`11041163-0`, energy 14366 J, time 56.64 s, power 253.62 W. Treat those
as the picture on the slide. A learner&rsquo;s job produces different
numbers, and the extracted slide text is too scrambled to grade against
a full column layout.

EAR and `eacct` are absent on the course cluster. Skip the exercise
there. Core-hours from `sacct` are the usage figure the cluster does
record.


<a id="orge097e2a"></a>

# Job arrays and QCG-PilotJob

QCG on Snellius stays on the 2024 stack, because EESSI has no 2025
build of QCG-PilotJob:

    module load 2024
    module load QCG-PilotJob/0.14.1-gfbf-2024a

On the course cluster replace both lines with:

    module load 2025
    module load QCG-PilotJob/0.14.1-GCCcore-14.2.0

Leave `modules=` off the individual tasks so they inherit the job
environment. A per-task module load is where most of the published QCG
idle time came from.

The climate files have 1000 CSVs. The mean used everywhere is the mean
of the second column. The first four, which every small run should
reproduce, are:

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-right" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">File</th>
<th scope="col" class="org-right">Mean</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">AGM00060355</td>
<td class="org-right">25.336749116607773</td>
</tr>


<tr>
<td class="org-left">AM000037704</td>
<td class="org-right">17.46982456140351</td>
</tr>


<tr>
<td class="org-left">ASN00001006</td>
<td class="org-right">34.76175438596491</td>
</tr>


<tr>
<td class="org-left">ASN00005007</td>
<td class="org-right">32.391349480968856</td>
</tr>
</tbody>
</table>

`prepare_input.sh` prefixes an index, so the array jobs see
`0_AGM00060355.csv`. `average.py` prints `dataset,mean` using the
basename without `.csv`.


<a id="orgf093b4d"></a>

## Example 1, a twelve-task array

Status: run

`hands-on/example_01/array_job.sh` is `--array 0-11%3` on `rome`, one
task, ten minutes. It prints the hostname, `$TMPDIR`, and the five
`SLURM_ARRAY_*` variables.

    cd hands-on/example_01
    sbatch array_job.sh

Output shape:

-   Twelve files, `slurm-<jobid>_<task>.out`, task ids 0 through 11.
-   At most three of them run at once (`%3`).
-   On one node every hostname line is the same. Across a cluster they
    may differ, and that is allowed.
-   Each file reports a different `$TMPDIR`, and the directory name
    contains the job id of that array task.
-   `SLURM_ARRAY_JOB_ID` is the shared id. `SLURM_ARRAY_TASK_COUNT` is
    
    1.  `SLURM_ARRAY_TASK_MAX` is 11. `SLURM_ARRAY_TASK_MIN` is 0.
    
    `SLURM_ARRAY_TASK_ID` is that file&rsquo;s index.

Here all twelve completed on `cursor`, task 0 reported `TMPDIR
/tmp/slurm-23`, count 12, max 11, min 0.

The copy of `array_job.sh` in this tree has a non-breaking space before
`$SLURM_ARRAY_TASK_ID`, `$SLURM_ARRAY_TASK_MAX` and
`$SLURM_ARRAY_TASK_MIN`. The variables still expand. The corrected
script uses an ordinary space, and that is the output to expect. A
learner who sees a slightly wide gap in those three labels has the
unfixed file; the values are still right.

On the course cluster `rome` is an alias. On a plain Magic Castle drop
`-p rome`. `$TMPDIR` there is the private `/tmp` or, on the course
cluster, `/localscratch/$USER.$SLURM_JOB_ID.0`.


<a id="org668d7a6"></a>

## Example 2, averages with an array

Status: run

    cd hands-on/example_02
    ./prepare_input.sh
    sbatch array_job.sh          # --array 0-999%10
    # when every task has left the queue:
    ./aggregate.sh <jobid>

`array_job.sh` loads `2025` and `Python/3.13.1-GCCcore-14.2.0` on
separate lines, copies `input_mod` and `average.py` into `$TMPDIR`, and
averages `input_mod/${SLURM_ARRAY_TASK_ID}_*.csv`.

Output shape: 1000 files `slurm-<jobid>_<task>.out`. Each contains
`TMPDIR = <path>` and `Analyzing file: input_mod/<index>_<station>.csv`
followed by `<index>_<station>,<mean>`. `aggregate.sh <jobid>` writes
`result.csv` with 1000 rows, one per station, and prints the station
names as it goes. A second job id does not leak into that file:
`aggregate.sh` truncates `result.csv` and reads only
`slurm-<jobid>_*.out`.

`aggregate.sh` also expands an unquoted variable in one `echo`. With a
matching file in the current directory that echo can turn into a
pathname. The mean line is still parsed from the output file. Grade the
`result.csv` rows.

Here a three-task array (`0-2%2`), submitted from `example_02`, wrote
three rows whose means match the table above, including the `0_`, `1_`
and `2_` prefixes. The full 1000-task array was not run. A fixture with
two job ids confirmed that `aggregate.sh 111` kept only `0_alpha` and
`1_beta`, and a later `aggregate.sh 222` replaced the file with
`9_other` only.

SBU question: `sacct -X --format=JobID%24,Timelimit,AllocCPUS,CPUTime,CPUTimeRAW -j <jobid>`.
`CPUTimeRAW` is core-seconds. Divide by 3600. The worked example in the
module is 7232 core-seconds, which is 2.01 core-hours; the text rounds
the illustration to 2.0 SBU. On the course cluster report that quotient
as core-hours and do not call it an SBU. `sacct` on this machine has no
accounting store, so the sample number was not remeasured.


<a id="orgfac168f"></a>

## Example 3, five hundred and twelve short tasks

Status: run

`qcg_job.sh` loads the QCG module and runs `qcg_job.py`, which creates
`output/` and submits 512 `hostname` tasks.

Output shape: `output/` contains `job.<i>.out` and `job.<i>.err` for
`i` from 0 to 511. The `.out` files each hold one hostname. The `.err`
files are empty. The submission directory also gains the QCG service
logs. 512 tasks in one allocation is the point: a job array would have
queued 512 separate allocations.

Here the 512-task script finished with 512 output files and a single
hostname, and a 16-task copy had empty error files. Both were run with
the installed QCG-PilotJob package.

On the course cluster use the site QCG module from the start of this
section, and `--ntasks=2` so the pilot fits a 2-core node. The 512
tasks then share those two cores.


<a id="org3427341"></a>

## Example 4, why the versions change

Status: run

`qcg_job.sh` runs `qcg_job_v1.py`. The other versions are commented
next to it. `QCG_MAX_INPUTS` limits how many CSVs are used; unset, the
scripts take all 1000.

Each version submits one average per file and then one aggregation.

-   v0 builds the aggregate command as `cat average_*.csv` and does not
    set `after`. The shell glob of 1000 paths can exceed the argument
    limit, and nothing stops the aggregate from starting before a late
    average. The comment in the source says `CVS`. On a quiet machine
    with four files the aggregate happened to see every file: that does
    not make v0 correct.
-   v1 sets `after` to the average job names, so the aggregate waits.
    This is the version the shipped script runs.
-   v2 submits the averages, waits, then submits the aggregate, in two
    waves.
-   v3 uses one `Jobs` object, `wait4all`, and `jobs.clear()` between the
    waves.
-   v4 keeps a task only when it finished with success, writes
    `selected.json` in a fresh `qcg-averages-*` directory, and runs
    `aggregate.py` on that directory. A missing file or a malformed mean
    fails the run instead of producing a short `result.csv`. The shell
    never sees 1000 path arguments.

Output shape for a successful v1 or v4 run: `results/result.csv` (v1)
or `result.csv` (v4) with one `station,mean` row per input, means
matching the table. v4&rsquo;s row order is the sorted station name.

Here v0 and v4 were run on the four files outside Slurm, and v1 was
submitted with `sbatch --ntasks=2` from `example_04` under
`QCG_MAX_INPUTS=4`. All three wrote the same four means. The full
1000-file run was not repeated.


<a id="orgb66b79b"></a>

## Example 5, the sleep pipeline

Status: run

`sleep.py <seconds>` prints one line:

    TASK,<cpu>,<start>,<end>

with `end - start` equal to the requested seconds, within a few
milliseconds. `pipeline.sh` reads `times.txt` (160 sleeps, 1128 seconds
in total) or `$TIMES_FILE`. `times_short.txt` is the first 32 sleeps,
338 seconds. The script prints `START,<epoch>`, runs as many sleeps at
once as it has tasks, then prints `END,<epoch>`.

`qcg_job.sh` does the same work through QCG. `plot_profile.py <log>`
writes a PNG with one lane per CPU.

Output shape of a log:

    START,<epoch seconds>
    TASK,<cpu>,<start>,<end>
    ...
    END,<epoch seconds>

The span is `END - START`. Idle time is the span times the number of
slots, minus the sum of the sleep lengths, as a percentage of the span
times the slots. Perfect packing of 338 seconds onto 2 slots takes at
least 169 seconds; the rest of a longer span is idle and overhead.

The published course-cluster measurement, 32 tasks and 2 slots, which
was not remeasured here:

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />

<col  class="org-right" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Tool</th>
<th scope="col" class="org-left">Span</th>
<th scope="col" class="org-right">Idle</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">bash pipeline</td>
<td class="org-left">266 s</td>
<td class="org-right">36%</td>
</tr>


<tr>
<td class="org-left">QCG-PilotJob</td>
<td class="org-left">221 s</td>
<td class="org-right">23%</td>
</tr>


<tr>
<td class="org-left">HyperQueue</td>
<td class="org-left">172 s</td>
<td class="org-right">2%</td>
</tr>


<tr>
<td class="org-left">Snakemake</td>
<td class="org-left">172 s</td>
<td class="org-right">2%</td>
</tr>
</tbody>
</table>

Most of that QCG idle time was a module load inside every task. The
scripts in this tree omit `modules=`, so a new QCG run should sit
closer to the HyperQueue and Snakemake rows.

Here `pipeline.sh` with a four-line stand-in (`0`, `1`, `0`, `1`) and
`--ntasks=2` printed `START`, four `TASK` lines and `END` two seconds
later, in two waves. `plot_profile.py` wrote a PNG. The full `times.txt`
and `times_short.txt` sleeps were not executed. `python` has to be on
`PATH` inside the job; the `Python/3.13.1-GCCcore-14.2.0` module
provides it. A job whose `PATH` has only `python3` prints `python:
command not found` and an `END` line with no `TASK` lines.

SBU, or core-hours: same `sacct` division as example 2, once per
pipeline. On the course cluster call the result core-hours.


<a id="org5613698"></a>

# HyperQueue, Snakemake and FireWorks

Same two workloads as examples 4 and 5. Each `average.sh` honours
`QCG_MAX_INPUTS` and otherwise takes 100 of the 1000 files. Each
`profile.sh` reads `$TIMES_FILE` and otherwise `times_short.txt`.

Load on the course cluster, each tool on its own line after
`module load 2025`:

-   `HyperQueue/0.24.0`
-   the Snakemake module the site provides (the hands-on asks for 9.22.0;
    a later 9.x runs the same `Snakefile`)
-   the FireWorks module the site provides

Snellius timings from the hands-on, for orientation: FireWorks, one
worker, 9 s for 100 files and 212 s for 1000; Snakemake, 15 s for 1000
files on 16 cores. FireWorks with a file-backed LaunchPad runs one
worker. `rlaunch multi` is not the setup to demonstrate.


<a id="org266f7ae"></a>

## HyperQueue

Status: run

`average.sh` starts a server and a worker, submits one job per CSV,
submits the aggregate with a dependency on all of them, and waits.

Output shape: `hq job list` shows every average `FINISHED`, then the
aggregate. `result.csv` has one row per input file, with the means from
the table. The server log may say the worker connected from an
unknown allocation when Slurm accounting is off; the tasks still
finish.

Here, four files: 4 tasks `FINISHED` and `result.csv` had 4 rows.


<a id="orgd1112dd"></a>

## Snakemake

Status: run

The `Snakefile` rule `average` takes one CSV and writes
`averages/<station>.csv`. The `aggregate` rule takes every average as
input. `average.sh` runs `snakemake --cores <n> aggregate`.

Output shape: the log lists one `average` job per file and then
`aggregate`. A second run with nothing changed prints `Nothing to be
done`. `result.csv` has the same rows as the other tools.

Here Snakemake 9.27.2 with two cores and four files ran four averages
and the aggregate. The means match the table. A later `sbatch` found
the outputs already present and did no work, which is the dependency
check the exercise is about.


<a id="orgab975c6"></a>

## FireWorks

Status: run

`workflow.py` builds one Firework per average plus one aggregate
Firework that depends on them, against a file LaunchPad
(`MONGOMOCK_SERVERSTORE_FILE`). `average.sh` calls `rlaunch rapidfire`,
which runs those Fireworks one at a time.

Output shape: `added <n> averages and the aggregation`, then one
`RUNNING fw_id` block per Firework, then `completed <n+1> Fireworks`
and a `result.csv` with `n` rows.

Here the Slurm script completed 5 Fireworks and wrote 4 rows. The
script calls `python`. The course `Python` module supplies that name.
A `PATH` that only has `python3` fails with `python: command not
found` before any Firework runs.


<a id="orgbd45620"></a>

## Questions

Status: run

1.  The shortest expression of &ldquo;aggregate after every average&rdquo; is the
    Snakemake rule whose `input` is the list of average outputs: the
    dependency is the filenames, and there is no extra edge to declare.
    HyperQueue adds one `--dep` (or equivalent) on the aggregate job.
    FireWorks sets the aggregate&rsquo;s parents to the average Fireworks.
    `qcg_job_v0.py` declares no dependency at all, which is the bug the
    earlier exercise asks learners to find. v1 adds `after`.

2.  The least idle time in the published 32-task table is HyperQueue
    and Snakemake, both at 2%. The bash pipeline packs poorly because a
    wave cannot start until the longest sleep in the previous wave
    ends. The QCG figure in that table is inflated by a per-task module
    load that the current scripts no longer do. The plots should show
    the bash gaps at the end of each wave, and the QCG gaps (in that
    older run) before each task&rsquo;s useful sleep.

3.  Core-hours are `CPUTimeRAW / 3600` from
    `sacct -X --format`&ldquo;JobID%24,Timelimit,AllocCPUS,CPUTime,CPUTimeRAW&rdquo; -j <jobid>=.
    Two cores held for 172 seconds is `344 / 3600 = 0.096` core-hours.
    On Snellius the same quotient is the SBU cost of the job. This
    machine cannot run `sacct`, so the arithmetic was checked and the
    query was not.


<a id="orgff7b9f7"></a>

# What was executed

<table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">


<colgroup>
<col  class="org-left" />

<col  class="org-left" />
</colgroup>
<thead>
<tr>
<th scope="col" class="org-left">Exercise</th>
<th scope="col" class="org-left">Status</th>
</tr>
</thead>

<tbody>
<tr>
<td class="org-left">Login identity, <code>env</code>, <code>NEWVAR</code>, <code>last</code></td>
<td class="org-left">run</td>
</tr>


<tr>
<td class="org-left"><code>myquota</code>, <code>accinfo</code></td>
<td class="org-left">not-run</td>
</tr>


<tr>
<td class="org-left">OpenMP hello, <code>python.sh</code>, <code>pi.sh</code></td>
<td class="org-left">run</td>
</tr>


<tr>
<td class="org-left"><code>sacct</code>, <code>seff</code>, <code>gpu.sh</code>, <code>nvidia-smi</code></td>
<td class="org-left">not-run</td>
</tr>


<tr>
<td class="org-left">One-minute job, dependency, <code>srun</code> versus bare <code>hostname</code> versus <code>mpirun</code></td>
<td class="org-left">run</td>
</tr>


<tr>
<td class="org-left">Mail notifications, eight tasks, a second node</td>
<td class="org-left">not-run</td>
</tr>


<tr>
<td class="org-left">R template</td>
<td class="org-left">not-run</td>
</tr>


<tr>
<td class="org-left">Filesystem tasks, <code>chmod 644</code>, <code>df</code> / <code>du</code></td>
<td class="org-left">run</td>
</tr>


<tr>
<td class="org-left">Job-local <code>$TMPDIR</code>, <code>print-n</code> at <code>n = 1000</code></td>
<td class="org-left">run</td>
</tr>


<tr>
<td class="org-left"><code>/gpfs</code> leftover search, <code>--constraint=scratch-node</code></td>
<td class="org-left">not-run</td>
</tr>


<tr>
<td class="org-left">Thousand-file transfer, twenty-thousand-file transfer, interrupted <code>rsync</code></td>
<td class="org-left">run</td>
</tr>


<tr>
<td class="org-left"><code>stage.slurm</code> with the scratch-node constraint</td>
<td class="org-left">not-run</td>
</tr>


<tr>
<td class="org-left"><code>pigz</code> and <code>zstd</code> on random bytes</td>
<td class="org-left">run</td>
</tr>


<tr>
<td class="org-left"><code>load_modules.sh</code>, sequential axpy, dot, matmul <code>n = 40</code></td>
<td class="org-left">run</td>
</tr>


<tr>
<td class="org-left">Hybrid axpy and dot kernels via <code>mpirun</code></td>
<td class="org-left">run</td>
</tr>


<tr>
<td class="org-left">Those kernels via the published <code>srun</code></td>
<td class="org-left">the launch failed in <code>MPI_Init</code></td>
</tr>


<tr>
<td class="org-left">Timing tables, 128-core columns, <code>N = 10^9</code> and above</td>
<td class="org-left">not-run</td>
</tr>


<tr>
<td class="org-left">Amdahl, Gustafson, flop counts, roofline ratio</td>
<td class="org-left">run, from the formulas</td>
</tr>


<tr>
<td class="org-left">uProf, <code>hwperf</code>, <code>valgrind</code>, EAR, <code>eacct</code></td>
<td class="org-left">not-run</td>
</tr>


<tr>
<td class="org-left">Array of 12, array of 3 plus <code>aggregate.sh</code>, two-job fixture</td>
<td class="org-left">run</td>
</tr>


<tr>
<td class="org-left">Array of 1000</td>
<td class="org-left">not-run</td>
</tr>


<tr>
<td class="org-left">QCG examples 3, 4 (v0, v1, v4 on 4 files) and 5 (4 short sleeps)</td>
<td class="org-left">run</td>
</tr>


<tr>
<td class="org-left">Full <code>times.txt</code> and the published idle-time table</td>
<td class="org-left">not-run, table quoted</td>
</tr>


<tr>
<td class="org-left">HyperQueue, Snakemake, FireWorks averages on 4 files</td>
<td class="org-left">run</td>
</tr>


<tr>
<td class="org-left">Their profile jobs at the published lengths</td>
<td class="org-left">not-run</td>
</tr>
</tbody>
</table>

