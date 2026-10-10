# Notes for trainers

These notes cover the cluster side of the module. The participant text is in `README.md`.

## Accounts

Magic Castle creates the guest accounts `user01` to `userNN` in FreeIPA, with `NN` set by `nb_users` in the cluster profile. All guests share one password. After `terraform apply` and the Puppet run, print the list:

```
surfcontroller-mc accounts cluster.toml -o tf           # names only
surfcontroller-mc accounts cluster.toml -o tf --show --csv accounts.csv
```

The CSV file contains the password and gets mode 0600. Hand out one account per participant and delete the file after the course.

Each account belongs to the group `def-sponsor00`, which is also its Slurm account. Because of that account, jobs need no `-A` option, and `/project/def-sponsor00` (linked as `~/projects/def-sponsor00`) is the shared project directory used in the exercises.

## Storage and quotas

Magic Castle does not enable quotas on its network file system (NFS) exports. All guests share the `home`, `project` and `scratch` volumes from the cluster profile, so size them for the whole group: exercise 1 writes up to 800 MB per run at the default `nmax`, so 20 participants need about 16 GB free on `/home`. One participant can fill a volume for everyone; check with `df -h /home /scratch /project` during the session.

Nothing is backed up. `terraform destroy` removes the volumes with the cluster.

## Slurm

* Jobs without `-p` go to the default partition, `cpubase_bycore_b1`, which contains all compute nodes.
* The default time limit is one hour, and the default memory is 256 MB per CPU. The exercise script `ex1/run.sh` asks for `--mem=2G`; keep that line if you raise `iend`.
* Each job gets node-local space in `/localscratch/$USER.$SLURM_JOB_ID.0` and a private `/tmp`, both removed at the end of the job. Magic Castle does not set `TMPDIR` for jobs.

## Software

The cluster loads the European Environment for Scientific Software Installation (EESSI) at login, and the version comes from the cluster profile (2025.06 or 2023.06). `ex1/run.sh` loads `GCC/14.3.0`, which is in 2025.06; on 2023.06 use the commented `GCC/13.2.0` line instead.

The JupyterHub form lists RStudio and code-server. EESSI has an `RStudio-Server` module but no `code-server` module, so tell participants not to pick code-server.

## Web access and certificates

JupyterHub, the FreeIPA portal and Mokey need Domain Name System (DNS) names for the login node. With `dns.mode = "sslip"` the names come from sslip.io and need no zone of your own. The web server then asks Let's Encrypt for certificates under `sslip.io`, a domain that is not on the Public Suffix List, so every sslip.io user draws from the same Let's Encrypt limit of 50 certificates per week. Test the web pages the day before the course, and use your own domain when you can.
