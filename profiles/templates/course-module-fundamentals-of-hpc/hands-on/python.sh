#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=00:02:00
#SBATCH --partition={{partitions.cpu}}
set -euo pipefail
module load {{modules.stack}}
module load {{modules.python}}
srun python3 -c 'import platform; print("Python on", platform.node()); print("sum:", sum(range(1000000)))'
