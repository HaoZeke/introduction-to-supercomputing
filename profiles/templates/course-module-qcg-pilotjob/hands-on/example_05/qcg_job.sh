#!/bin/bash
#SBATCH --nodes={{jobs.qcg.example_05.nodes}}
#SBATCH --ntasks={{jobs.qcg.example_05.ntasks}}
#SBATCH --time=00:40:00
#SBATCH --partition={{partitions.cpu}}
#SBATCH --output=qcg.%j.out
#SBATCH --error=qcg.%j.err

# QCG-PilotJob comes from the course CernVM-FS repository.
_course_restore_nounset=0
case $- in *u*) _course_restore_nounset=1; set +u ;; esac
source {{modules.eessi_init}}
if [ "$_course_restore_nounset" = 1 ]; then set -u; fi
unset _course_restore_nounset
module use {{modules.site_modulepath}}
module load {{modules.qcg}}

START=$( date +%s )
python qcg_job.py
END=$( date +%s )

# concatenate all output files
echo START,$START
cat $TMPDIR/qcg_*.out
echo END,$END
