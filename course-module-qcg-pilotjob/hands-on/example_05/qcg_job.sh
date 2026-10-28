#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --time=00:40:00
#SBATCH --partition=rome
#SBATCH --output=qcg.%j.out
#SBATCH --error=qcg.%j.err

# QCG-PilotJob comes from the course CernVM-FS repository.
_course_restore_nounset=0
case $- in *u*) _course_restore_nounset=1; set +u ;; esac
source /cvmfs/software.eessi.io/versions/2025.06/init/lmod/bash
if [ "$_course_restore_nounset" = 1 ]; then set -u; fi
unset _course_restore_nounset
module use /cvmfs/course.surf-src.cvmfs/eessi/versions/2025.06/software/linux/x86_64/amd/zen2/modules/all
module load QCG-PilotJob/0.14.1-GCCcore-14.2.0

START=$( date +%s )
python qcg_job.py
END=$( date +%s )

# concatenate all output files
echo START,$START
cat $TMPDIR/qcg_*.out
echo END,$END
