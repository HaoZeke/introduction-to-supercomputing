#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=00:20:00
#SBATCH --partition=rome
#SBATCH --output=fw-average.%j.out
# Example 4 with FireWorks: the workflow goes into a LaunchPad, then workers in this
# allocation run whatever is ready until nothing is left.
set -euo pipefail
module load 2025
module load FireWorks/2.1.4-gfbf-2025a

export MONGOMOCK_SERVERSTORE_FILE=$TMPDIR/launchpad.json
tar -xf ../../example_04/input.tar.gz
python workflow.py average
cd "$TMPDIR"   # rlaunch makes a directory per Firework run
rlaunch multi "$SLURM_NTASKS"
lpad get_fws -d count -s COMPLETED
cd - >/dev/null
echo "result.csv: $(wc -l < result.csv) rows"
