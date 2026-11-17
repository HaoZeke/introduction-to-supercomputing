#!/bin/bash
#SBATCH --nodes={{jobs.qcg.example_03.nodes}}
#SBATCH --ntasks-per-node={{jobs.qcg.example_03.ntasks_per_node}}
#SBATCH --time=00:05:00
#SBATCH --partition={{partitions.cpu}}

# QCG-PilotJob comes from the course CernVM-FS repository.
_course_restore_nounset=0
case $- in *u*) _course_restore_nounset=1; set +u ;; esac
source {{modules.eessi_init}}
if [ "$_course_restore_nounset" = 1 ]; then set -u; fi
unset _course_restore_nounset
module use {{modules.site_modulepath}}
module load {{modules.qcg}}

python3 qcg_job.py

