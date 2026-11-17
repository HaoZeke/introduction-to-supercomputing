#!/bin/bash
#SBATCH --nodes={{jobs.qcg.snakemake_profile.nodes}}
#SBATCH --ntasks={{jobs.qcg.snakemake_profile.ntasks}}
#SBATCH --time=00:40:00
#SBATCH --partition={{partitions.cpu}}
#SBATCH --output=snakemake.%j.out
#SBATCH --error=snakemake.%j.err
set -euo pipefail
module load {{modules.stack}}
# SRC course cluster: module. {{system.display_name}} has no snakemake module: use the venv from the README.
module load {{modules.snakemake}} 2>/dev/null || { module load {{modules.python}}; source "$HOME/venvs/snakemake/bin/activate"; }

rm -rf profile
echo START,$(date +%s)
snakemake --snakefile Snakefile.profile --cores "$SLURM_NTASKS" >&2
echo END,$(date +%s)
cat profile/*.out
