#!/bin/bash
#SBATCH --nodes={{jobs.qcg.fireworks_profile.nodes}}
#SBATCH --ntasks={{jobs.qcg.fireworks_profile.ntasks}}
#SBATCH --time=00:40:00
#SBATCH --partition={{partitions.cpu}}
#SBATCH --output=fw.%j.out
#SBATCH --error=fw.%j.err
# One worker: the file-backed LaunchPad loses Firework states with several rlaunch workers,
# so the tasks run one after another. Parallel workers need a MongoDB server.
set -euo pipefail
_course_restore_nounset=0
case $- in *u*) _course_restore_nounset=1; set +u ;; esac
source {{modules.eessi_init}}
if [ "$_course_restore_nounset" = 1 ]; then set -u; fi
unset _course_restore_nounset
module use {{modules.site_modulepath}}
# SRC course cluster: module. {{system.display_name}} has no FireWorks module: use the venv from the README.
module load {{modules.fireworks}} 2>/dev/null || { module load {{modules.python}}; source "$HOME/venvs/fireworks/bin/activate"; }

run_dir=$(mktemp -d "$TMPDIR/fw-profile.XXXXXXXX")
export MONGOMOCK_SERVERSTORE_FILE=$run_dir/launchpad.json TASK_DIR=$run_dir/tasks
echo "{}" > "$MONGOMOCK_SERVERSTORE_FILE"
python workflow.py profile >&2
echo START,$(date +%s)
(cd "$TMPDIR" && rlaunch rapidfire >&2)
python workflow.py check >&2
echo END,$(date +%s)
cat "$TASK_DIR"/*.out
