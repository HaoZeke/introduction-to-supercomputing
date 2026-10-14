#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=00:20:00
#SBATCH --partition=rome
#SBATCH --output=snakemake-average.%j.out
set -euo pipefail
module load 2025
module load snakemake/9.22.0-foss-2025b

tar -xf ../../example_04/input.tar.gz
# Snakemake runs the rules inside this allocation, on as many cores as Slurm gave the job
snakemake --snakefile Snakefile --cores "$SLURM_NTASKS"
echo "result.csv: $(wc -l < result.csv) rows"
