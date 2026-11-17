# Hands-on fundamentals of high-performance computing

This hands-on session introduces **basic usage of the {{system.display_name}} supercomputer at SURF**. You will learn how to:
* connect to {{system.display_name}},
* understand the Linux environment,
* navigate the file system,
* compile a simple parallel program,
* submit and monitor jobs using the SLURM workload manager.

---

## 1. Accessing {{system.display_name}} and exploring the Linux environment

**Objective:** Connect to {{system.display_name}} and retrieve basic system and user information. Verify your access and become familiar with the Linux environment. Record this information in a text file called `<username>.dat` located in your home directory.
 
| #  | Question                                      | Command                               | Environment variable |
|----|-----------------------------------------------|---------------------------------------|----------------------|
| 1  | What is your username?                        | `whoami`                              | `echo $USER`         |
| 2  | What is your current working directory?       | `pwd`                                 | `echo $PWD`          |
| 3  | What is your home directory?                  | _none_                                | `echo $HOME`         |
| 4  | Which login node are you on?                  | `hostname`                            | `echo $HOSTNAME`     |
| 5  | When did you last log in to {{system.display_name}}?         | `last -n 1 -R $USER`                  | _none_               |
| 6  | How much storage quota do you have?           | `{{commands.quota}}`                             | _none_               |
| 7  | What is your compute budget and usage?        | `{{commands.accounting}}`                             | _none_               |

### 1.1. Connecting to {{system.display_name}}

To access {{system.display_name}}, connect via SSH ([troubleshooting guide](https://servicedesk.surf.nl/wiki/spaces/WIKI/pages/30660265/{{system.display_name}}+FAQ#{{system.display_name}}FAQ-Troublewithconnectingto{{system.display_name}})):

```
$ ssh <username>@{{system.login_host}}
```

{{#asides}}
{{fundamentals.aside_note}}

{{/asides}}
{{^asides}}
{{fundamentals.self_note}}

{{/asides}}
When you log in, you are placed on a login node (for example {{system.login_node_first}} or {{system.login_node}}), and **interact with the system through a shell**. The shell interprets your **commands**, executes **programs**, and provides access to your **environment** variables: named values that configure your session.

### 1.2. Creating your first file

> 🖥️ **Editing files in the Shell**
>
> There are multiple ways to edit files in a Shell. Two common options are:
> * Shell editors like [`vim`](https://www.vim.org) or [`nano`](https://www.nano-editor.org), for manual editing.
> * Output [redirection](https://www.gnu.org/software/bash/manual/html_node/Redirections.html) using `>` for overwriting or `>>` for appending.

After connecting to {{system.display_name}}, your Shell will be located at your home directory: `/home/<username>`. Let’s create a new text file where you will store all your answers for this section.

```
[<username>@{{system.login_node}} ~]$ touch <username>.dat
[<username>@{{system.login_node}} ~]$ ls
<username>.dat
```

Now every time you obtain a piece of information, append it to your file using, for instance, the >> redirection operator:

```
[<username>@{{system.login_node}} ~]$ echo "Username: $USER" >> <username>.dat
[<username>@{{system.login_node}} ~]$ cat <username>.dat
Username: <username>
```

### 1.3. Understanding the Linux environment

> 📦 **Why do environment variables exist?**
> 
> You’re working on a shared system ({{system.display_name}}), with thousands of users and hundreds of programs. Every time you run a program, it needs to know who you are, where your files are, what software you use, what language or region settings you prefer.
> 
> Typing these details every single time would be painful and error-prone. That’s where environment variables come in: they act as a set of predefined, user-specific values that make the shell context-aware and help programs behave correctly without manual input every time.
> 
> Let’s say John Doe wants to create a folder for logs and save a file there. John could hardcode:
> ```
> [<username>@{{system.login_node}} ~]$ mkdir /home/johnd/logs
> [<username>@{{system.login_node}} ~]$ echo "My log entry" > /home/johnd/logs/run.log
> ```
> 
> But this will fail for everyone else, because `/home/johnd/` only works for John. Instead, John could use the environment variable `$HOME`, which automatically expands to the correct home directory for any user:
> ```
> [<username>@{{system.login_node}} ~]$ mkdir -p $HOME/logs
> [<username>@{{system.login_node}} ~]$ echo "My log entry" > $HOME/logs/run.log
> ```
> 
> ✅ Now the script works for everyone, not just John. This is essential in shared environments, job scripts, and automation.

#### 1.3.1. Exploring the Linux environment

**Environment variables determine how the shell behaves**. They tell programs where to look for files, which compiler to use, what language to display messages in, and more. You can inspect the environment defined in your session using the env command:
```
[<username>@{{system.login_node}} ~]$ env
SHELL=/bin/bash
USER=<username>
HOME=/home/<username>
PATH=/home/<username>/.local/bin:/usr/local/bin:/usr/bin:/bin
...
```

The method above is very verbose. Instead, let’s record a few key ones in the file: 
```
[<username>@{{system.login_node}} ~]$ echo "Current directory: $PWD" >> <username>.dat
[<username>@{{system.login_node}} ~]$ echo "Home directory: $HOME" >> <username>.dat
[<username>@{{system.login_node}} ~]$ echo "Login node: $HOSTNAME" >> <username>.dat
[<username>@{{system.login_node}} ~]$ cat <username>.dat
Username: <username>
Current directory: /home/<username>
Home directory: /home/<username>
Login node: {{system.login_node_fqdn}}
```

#### 1.3.2. Modifying the Linux environment

**Environment variables only exist within your current shell session**. When you log out or launch a separate process, a new environment is created and does not automatically inherit the variables you changed manually—unless you explicitly export or pass them. Let’s explore this through two small experiments.

Create a variable in your current session and print its value. Then exit the session, log in again, and print the value again.
```
[<username>@{{system.login_node}} ~]$ NEWVAR="Hello_123"
[<username>@{{system.login_node}} ~]$ echo $NEWVAR
Hello_123
[<username>@{{system.login_node}} ~]$ exit
logout
$ ssh <username>@{{system.login_host}}
[<username>@{{system.login_node}} ~]$ echo $NEWVAR
```

The output is empty. **The variable `NEWVAR` is gone because the environment was destroyed when the session ended**. If you want a variable to appear automatically in every new login, you must define it in one of your shell startup files (for example `~/.bash_profile` or `~/.bashrc`).

#### 1.4. Retrieving system and accounting information
While the environment provides user-specific information or shell configuration, other types of information are obtained from **extensive system logs and accounting databases**. These logs are maintained by the operating system or by {{system.display_name}}-specific services. System logs may include data such as your last login time or active sessions, while accounting logs store resource usage, storage quotas, or compute budgets.

On {{system.display_name}}, accounting information is collected and exposed through dedicated commands implemented by the system administrators. These tools retrieve data directly from the system’s internal accounting infrastructure and present it in a user-friendly format.

Finally, use the following commands to collect details about your quota and compute budgets, and include them to your log file:

```
[<username>@{{system.login_node}} ~]$ last -n 1 -R $USER
<username>  pts/5        Tue Oct 28 20:12   still logged in
[<username>@{{system.login_node}} ~]$ {{commands.quota}}
<username>@home6
  Quota                Limit                Usage               
  200.00 GiB           210.00 GiB           65.7232%        GiB        [===================           ]
  1000000 Inodes       1200000 Inodes       70.8850%        Inodes     [=====================         ]

[<username>@{{system.login_node}} ~]$ {{commands.accounting}}
```

Now you have a single file summarising your system and user environment on {{system.display_name}} — a simple but practical way to document what’s running under the hood.

---

## 2. Compiling and submitting a job

**Objective:** Compile a small OpenMP program on the login node, run it on a compute node through Slurm, and check what the job used.

### 2.1. Compiling a parallel program

Create a directory and a C file that prints one line per OpenMP thread:

```bash
mkdir -p $HOME/hello
cd $HOME/hello
cat > hello.c << 'END'
#include <stdio.h>
#include <omp.h>

int main(void)
{
    #pragma omp parallel
    printf("Hello from thread %d of %d\n", omp_get_thread_num(), omp_get_num_threads());
    return 0;
}
END
```

Load the 2025 software stack and its GCC compiler, then compile with OpenMP enabled:

```bash
module load {{modules.stack}}
module load {{modules.compiler}}
gcc -O2 -fopenmp hello.c -o hello
```

Compiling on the login node is fine. Running the program with many threads is not: that is what the compute nodes are for.

### 2.2. Submitting the job

Save the following job script as `hello.sh` in the same directory. It asks for {{jobs.fundamentals.hello.cpus_per_task}} cores on one `{{partitions.cpu}}` node, {{fundamentals.hello_why}}, and runs one thread per core:

```bash
#!/bin/bash
#SBATCH --job-name=hello
#SBATCH --partition={{partitions.cpu}}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={{jobs.fundamentals.hello.cpus_per_task}}
#SBATCH --time=00:05:00
#SBATCH --output=hello-%j.out

module purge
module load {{modules.stack}}
module load {{modules.compiler}}

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
./hello
```

Submit it and note the job ID that `sbatch` prints:

```bash
sbatch hello.sh
```

### 2.3. Monitoring the job

While the job waits or runs, `squeue` lists it. The `ST` column shows `PD` for pending and `R` for running:

```bash
squeue -u $USER
```

When the job has left the queue, read its output. It has {{jobs.fundamentals.hello.cpus_per_task}} lines, in a different order on every run:

```bash
cat hello-<jobid>.out
```

`sacct` reports the state and run time of a finished job, and `seff` how much of the requested CPU time and memory it used:

```bash
sacct -j <jobid> --format=JobID,JobName,Partition,AllocCPUS,State,Elapsed
seff <jobid>
```

A job that used a small share of the CPU time it asked for wastes budget. Ask for fewer cores next time, or check that the program uses all of them.

### 2.4. A first GPU job

GPU nodes have their own partitions, and a job has to ask for GPUs explicitly. Save this as `gpu.sh`:

```bash
#!/bin/bash
#SBATCH --job-name=gpu-hello
#SBATCH --partition={{partitions.gpu}}
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=00:05:00
#SBATCH --output=gpu-hello-%j.out

nvidia-smi
```

Submit it with `sbatch gpu.sh`. {{fundamentals.gpu_result}}
{{#asides}}

{{fundamentals.gpu_aside}}
{{/asides}}
