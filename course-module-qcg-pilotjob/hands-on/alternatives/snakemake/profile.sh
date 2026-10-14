#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=00:40:00
#SBATCH --partition=rome
#SBATCH --output=snakemake.%j.out
#SBATCH --error=snakemake.%j.err
set -euo pipefail
module load 2025
module load snakemake/9.22.0-foss-2025b

rm -rf profile
echo START,$(date +%s)
snakemake --snakefile Snakefile.profile --cores "$SLURM_NTASKS" >&2
echo END,$(date +%s)
cat profile/*.out
