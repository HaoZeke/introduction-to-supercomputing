#!/bin/bash
#SBATCH -J matmul              # Job name
#SBATCH -o matmul-%j.out       # Output log file (%j will be replaced with job ID)
#SBATCH -e matmul-%j.err       # Error log file (%j will be replaced with job ID)
{{#jobs.hybrid.ex5}}
#SBATCH --nodes={{nodes:<15}}# Number of nodes
#SBATCH --ntasks={{ntasks:<14}}# Total number of tasks (parallel processes)
#SBATCH --ntasks-per-node={{ntasks_per_node:<5}}# Number of tasks per node
#SBATCH --cpus-per-task={{cpus_per_task:<7}}# Number of CPU cores per task
{{/jobs.hybrid.ex5}}
#SBATCH --time=01:00:00        # Time limit (hh:mm:ss)

# Check if the N parameter was provided
if [ -z "$1" ]; then
    echo "Usage: sbatch submit-matmul.sh <N>"
    exit 1
fi

# Load necessary modules
module load {{modules.stack:<19}}# Load the specific environment (update as needed)
module load {{modules.toolchain:<19}}# Load the desired compiler/toolchain (update as needed)

# Compile the program
gcc -O2 matmul.c -o matmul.out     # Compile the matrix multiplication C program

# Execute the program with N passed as an argument
N=$1                           # Set the matrix size from the first command line argument
srun ./matmul.out $N           # Run the executable
