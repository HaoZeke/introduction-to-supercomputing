#!/bin/bash
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=128
#SBATCH --time=00:05:00
#SBATCH --partition=rome

# QCG-PilotJob comes from the course CernVM-FS repository.
_course_restore_nounset=0
case $- in *u*) _course_restore_nounset=1; set +u ;; esac
source /cvmfs/software.eessi.io/versions/2025.06/init/lmod/bash
if [ "$_course_restore_nounset" = 1 ]; then set -u; fi
unset _course_restore_nounset
module use /cvmfs/course.surf-src.cvmfs/eessi/versions/2025.06/software/linux/x86_64/amd/zen2/modules/all
module load QCG-PilotJob/0.14.1-GCCcore-14.2.0

python3 qcg_job.py

