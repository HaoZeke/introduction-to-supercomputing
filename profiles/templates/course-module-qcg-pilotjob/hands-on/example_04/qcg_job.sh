#!/bin/bash
#SBATCH --nodes={{jobs.qcg.example_04.nodes}}
#SBATCH --ntasks={{jobs.qcg.example_04.ntasks}}
#SBATCH --time=00:20:00
#SBATCH --partition={{partitions.cpu}}

# QCG-PilotJob comes from the course CernVM-FS repository.
_course_restore_nounset=0
case $- in *u*) _course_restore_nounset=1; set +u ;; esac
source {{modules.eessi_init}}
if [ "$_course_restore_nounset" = 1 ]; then set -u; fi
unset _course_restore_nounset
module use {{modules.site_modulepath}}
module load {{modules.qcg}}

echo $TMPDIR

# copy input data and scripts to working directory
cp -r $SLURM_SUBMIT_DIR/. $TMPDIR/
cd $TMPDIR

# execute jobs
# python3 qcg_job_v0.py
python3 qcg_job_v1.py
# python3 qcg_job_v2.py
# python3 qcg_job_v3.py
# python3 qcg_job_v4.py

# copy result back to submission directory
mkdir -p $SLURM_SUBMIT_DIR/results
cp result.csv  $SLURM_SUBMIT_DIR/results/

# archive the logdata for the reference
tar -c --exclude="input" --exclude="result" . > $SLURM_SUBMIT_DIR/results/log.${SLURM_JOB_ID}.tar
gzip $SLURM_SUBMIT_DIR/results/log.${SLURM_JOB_ID}.tar



