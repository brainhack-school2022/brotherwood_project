#!/bin/bash
#SBATCH --job preprocessing
#SBATCH --time 24:0:0
#SBATCH --account def-charesti
#SBATCH --array 1-272
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 16
#SBATCH --mem-per-cpu 4G
#SBATCH -o log/%x-%A-%a.out
#SBATCH -e log/%x-%A-%a.err

set -e

module load singularity/3.8

# replace following paths with those corresponding to your system

WKDIR=/home/${USER}/projects/def-charesti/pbro98/brotherwood_project
DATADIR=${WKDIR}/data
FSDIR=${WKDIR}/images
TFDIR=${WKDIR}/images/templateflow
SUB=$(sed -n ${SLURM_ARRAY_TASK_ID}p ${WKDIR}/valid_subjects.txt)

export SINGULARITYENV_TEMPLATEFLOW_HOME=/templateflow

echo -e "\n"
echo "Starting fmriprep.."
echo "subject: $SUB"
echo "working directory: $WKDIR"
echo "data directory: $DATADIR"
echo -e "\n"

singularity run --cleanenv -B $DATADIR:/data -B $TMPDIR:/work -B $TMPDIR:/tmp -B $FSDIR:/fs -B $TFDIR:/templateflow \
    ${WKDIR}/images/fmriprep-21.0.2.simg \
    /data/BIDS/ \
    /data/preprocessed/ \
    participant --participant-label $SUB --skip-bids-validation --work-dir /work/ --fs-license-file /fs/fs-license/license.txt --omp-nthreads $SLURM_CPUS_PER_TASK --nthreads $SLURM_CPUS_PER_TASK --mem-mb 30000 -vv
