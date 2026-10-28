#!/bin/bash
#SBATCH -J dot-hybrid          # Job name
#SBATCH -o dot-hybrid-%j.out   # Output log file (%j will be replaced with job ID)
#SBATCH -e dot-hybrid-%j.err   # Error log file (%j will be replaced with job ID)
{{#jobs.hybrid.ex4}}
#SBATCH --nodes={{nodes:<15}}# Number of nodes
#SBATCH --ntasks={{ntasks:<14}}# Total number of tasks (parallel processes)
{{#ntasks_per_node?}}
#SBATCH --ntasks-per-node={{ntasks_per_node:<5}}# Number of tasks per node
{{/ntasks_per_node?}}
#SBATCH --cpus-per-task={{cpus_per_task:<7}}# Number of OpenMP threads per MPI task
{{/jobs.hybrid.ex4}}
#SBATCH --time=01:00:00        # Time limit (hh:mm:ss)

# Check if the N parameter was provided
if [ -z "$1" ]; then
    echo "Usage: sbatch submit-dot-hybrid.sh <N>"
    exit 1
fi

# Load necessary modules
module load {{modules.stack}}
module load {{modules.toolchain}}

# Compile the program
mpicc -O2 -fopenmp dot-hybrid.c -o dot-hybrid.out -lm

# Set the OMP_NUM_THREADS environment variable to match the cpus-per-task
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Execute the program with N passed as an argument
N=$1                           # Set the vector size from the first command line argument
srun ./dot-hybrid.out $N       # Run the executable
