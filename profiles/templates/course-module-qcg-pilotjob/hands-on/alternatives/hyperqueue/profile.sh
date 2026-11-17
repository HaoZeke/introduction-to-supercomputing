#!/bin/bash
#SBATCH --nodes={{jobs.qcg.hyperqueue_profile.nodes}}
#SBATCH --ntasks={{jobs.qcg.hyperqueue_profile.ntasks}}
#SBATCH --time=00:40:00
#SBATCH --partition={{partitions.cpu}}
#SBATCH --output=hq.%j.out
#SBATCH --error=hq.%j.err
# Example 5 with HyperQueue: the same sleeping tasks, scheduled as soon as a core is free.
# TIMES_FILE picks the task lengths (default: example 5's times.txt).
set -euo pipefail
_course_restore_nounset=0
case $- in *u*) _course_restore_nounset=1; set +u ;; esac
source {{modules.eessi_init}}
if [ "$_course_restore_nounset" = 1 ]; then set -u; fi
unset _course_restore_nounset
module use {{modules.site_modulepath}}
# {{modules.hyperqueue}} exists on the SRC course cluster and on {{system.display_name}} (2025)
module load {{modules.python}} 2>/dev/null || true
module load {{modules.hyperqueue}}

export HQ_SERVER_DIR=$(mktemp -d "$TMPDIR/hq-profile.XXXXXXXX")
hq server start >&2 &
server_pid=$!
worker_pid=
trap 'rc=$?; trap - EXIT; hq server stop >/dev/null 2>&1 || true; kill "$server_pid" ${worker_pid:+"$worker_pid"} 2>/dev/null || true; wait || true; exit "$rc"' EXIT
for attempt in {1..60}; do
    hq server info >/dev/null 2>&1 && break
    kill -0 "$server_pid"
    sleep 1
done
hq server info >/dev/null
hq worker start --cpus="$SLURM_NTASKS" >&2 &
worker_pid=$!
hq worker wait 1 >&2

times=$(realpath "${TIMES_FILE:-../../example_05/times.txt}")
tasks=$(mktemp -d "$TMPDIR/hq-tasks.XXXXXXXX")
echo START,$(date +%s)
hq submit --each-line "$times" --cpus=1 --wait --stdout "$tasks/%{TASK_ID}.out" --stderr none \
    -- bash -c 'cd "$1" && python3 sleep.py "$HQ_ENTRY"' _ "$PWD/../../example_05" >&2
echo END,$(date +%s)
cat "$tasks"/*.out
hq server stop >&2
