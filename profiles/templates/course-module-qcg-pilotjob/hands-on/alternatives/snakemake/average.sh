#!/bin/bash
#SBATCH --nodes={{jobs.qcg.snakemake_average.nodes}}
#SBATCH --ntasks={{jobs.qcg.snakemake_average.ntasks}}
#SBATCH --time=00:20:00
#SBATCH --partition={{partitions.cpu}}
#SBATCH --output=snakemake-average.%j.out
set -euo pipefail
module load {{modules.stack}}
# SRC course cluster: module. {{system.display_name}} has no snakemake module: use the venv from the README.
module load {{modules.snakemake}} 2>/dev/null || { module load {{modules.python}}; source "$HOME/venvs/snakemake/bin/activate"; }

tar -xf ../../example_04/input.tar.gz
# Snakemake runs the rules inside this allocation, on as many cores as Slurm gave the job
snakemake --snakefile Snakefile --cores "$SLURM_NTASKS"
echo "result.csv: $(wc -l < result.csv) rows"
