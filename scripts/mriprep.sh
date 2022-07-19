#!/bin/bash
#SBATCH --job preprocessing
#SBATCH --time 24:0:0
#SBATCH --account def-charesti
#SBATCH --mem 32G
#SBATCH --array 1-259

set -e

module load singularity/3.8

workingdir=$(echo "/home/pbro98/projects/def-charesti/pbro98/brotherwood_project")
subject=$(sed -n ${SLURM_ARRAY_TASK_ID} ${workingdir}/valid_subjects.txt)

singularity run --cleanenv ${workingdir}/images/fmriprep-21.0.2.simg ${workingdir}/data/ds00030 ${workingdir}/data/preprocessed participant --participant-label ${subject}


