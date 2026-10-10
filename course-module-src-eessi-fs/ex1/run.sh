#!/bin/bash
#SBATCH -J ex1      # Job name
#SBATCH -t 00:15:00 # Max runtime in format HH:MM:SS
#SBATCH --mem=2G    # Magic Castle's default is 256 MB per CPU
# No -p: jobs go to the default partition, cpubase_bycore_b1

# EESSI is set up at login on a Magic Castle cluster with software_stack = "eessi".
# EESSI 2025.06:
module load GCC/14.3.0
# EESSI 2023.06 (Magic Castle's default), use instead:
# module load GCC/13.2.0

exec_name=print-n.out

gcc print-n.c -o ${exec_name}

# Array lenght <n> is calculated as 10**i
#  Use ibeg and iend to tune the range of i
#  Use nmax to limit the size of the output vector (10**8 results in 800 MB)
#  Raise iend and --mem together; compute nodes on a teaching cluster are small
ibeg=6
iend=9
nmax=$(( 10**8 ))

wdir=$HOME

for (( i = $ibeg; i < $iend; ++i ))
do
    n=$(( 10**$i ))

    if (( $n > $nmax )); then
        data=$(( $n*8/1000000000 ))
        echo "You are attempting to print too much data ($data GB)"
        exit 1
    fi

    srun ${exec_name} $n $wdir/ex1.dat ascii
    echo "Printing $n elements"
done
