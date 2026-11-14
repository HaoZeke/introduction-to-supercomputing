# Local stand-in for the Magic Castle file-system exercises

Two Slurm compute nodes, a login node that also runs `slurmctld`, and an
NFSv4 server for `/home`, `/project` and `/scratch`. The image builds
Compute Canada's `cc-tmpfs_mounts` SPANK plugin, turns on cgroup v2 memory
limits, and mounts EESSI 2025.06 with CernVM-FS. Run the course exercises
from the NFS home as `user01`.

This is not a Magic Castle deployment. Magic Castle 16.0.3 uses Slurm 26.05
and `auth/slurm`. Here the scheduler is the Ubuntu 24.04 package (Slurm
23.11) with munge, which is enough to run the hands-on. The NFS server is
nfs-ganesha because this kernel has an NFS client and no `nfsd`.

## Requirements

Docker with the compose plugin, and a privileged daemon. The host needs
`/dev/fuse`, cgroup v2 with the memory controller, and outbound HTTPS so the
nodes can mount `software.eessi.io`.

If container-to-container traffic dies while `iptables-legacy -S FORWARD`
starts with `-P FORWARD DROP`, the bridge is being dropped by the legacy
table. `scripts/up.sh` sets that policy to ACCEPT.

## Run

```bash
cd tools/mc-local-test
./scripts/up.sh
./scripts/run-checks.sh
./scripts/down.sh
```

`MC_NODES=1 ./scripts/up.sh` starts the login node and `node1` only. Slurm
still lists `node2`, so that name stays down and jobs run on `node1`.
`./scripts/run-checks.sh` submits every `#SBATCH` script in the course
README, `ex1/run.sh`, and the hands-on commands. `MC_SCOPE=ci` skips the
1000-file transfer. The client in the image is CernVM-FS 2.14.1 with
`cvmfs-config-eessi` 0.6.0. There is no systemd, so `entrypoint.sh` mounts
`software.eessi.io` itself.

`up.sh` writes `secrets/munge.key` on first use. Give the cluster a minute
the first time: each node mounts EESSI and fills its own CernVM-FS cache.

A shell on the login node:

```bash
sudo docker compose exec -u user01 login1 bash -l
```

`user01` is uid 60001, group `def-sponsor00`. Jobs go to the default
partition `cpubase_bycore_b1`. `DefMemPerCPU` is 256. `ConstrainRAMSpace=yes`,
so a step that passes its memory limit is OOM-killed.

At the end of a step, `slurmd` may log `Unable to move pid ... to init root
cgroup`. The step has already finished; the memory limit above still applies.

## Layout

| Service | Role |
|---|---|
| `mgmt1` | nfs-ganesha exports `/home`, `/project`, `/scratch` |
| `login1` | login node and `slurmctld` |
| `node1`, `node2` | `slurmd`, private `/localscratch`, EESSI |

The course tree is mounted at `/opt/course`. Copy it into `/home/user01`
before submitting so the working directory is on NFS.

## GitHub Actions

`.github/workflows/mc-local-test.yml` shellchecks the scripts and runs
`MC_NODES=1 MC_SCOPE=ci ./scripts/run-checks.sh`. Hosted runners guarantee
14 GB of disk, and 8 GB of memory on a private repository. The full run
adds a second compute node and five copies of a 1 GB incompressible tree,
which does not fit that guarantee. The workflow caches the image build.
