#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=00:40:00
#SBATCH --partition=rome
#SBATCH --output=fw.%j.out
#SBATCH --error=fw.%j.err
set -euo pipefail
module load 2025
# SRC course cluster: module. Snellius has no FireWorks module: use the venv from the README.
module load FireWorks/2.1.4-gfbf-2025a 2>/dev/null || source "$HOME/venvs/fireworks/bin/activate"

export MONGOMOCK_SERVERSTORE_FILE=$TMPDIR/launchpad.json TASK_DIR=$TMPDIR/tasks
echo "{}" > "$MONGOMOCK_SERVERSTORE_FILE"
python workflow.py profile >&2
echo START,$(date +%s)
(cd "$TMPDIR" && rlaunch multi "$SLURM_NTASKS" >&2)
echo END,$(date +%s)
cat "$TMPDIR"/tasks/*.out
