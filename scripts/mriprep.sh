  GNU nano 4.6                                                                                        mriprep.sh                                                                                                   
#!/bin/bash
#SBATCH --job preprocessing
#SBATCH --time 24:0:0
#SBATCH --account def-charesti
#SBATCH --array 1-259
#SBATCH --ntasks 1
#SBATCH --cpus-per-task 16
#SBATCH --mem-per-cpu 4G
#SBATCH -o log/%x-%A-%a.out
#SBATCH -e log/%x-%A-%a.err

set -e

module load singularity/3.8

WKDIR="/home/pbro98/projects/def-charesti/pbro98/brotherwood_project"
DATADIR=${WKDIR}/data
FSDIR=${WKDIR}/images/fs-license
SUB=$(sed -n ${SLURM_ARRAY_TASK_ID}p ${WKDIR}/valid_subjects.txt)

echo -e "\n"
echo "Starting fmriprep.."
echo "subject: $SUB"
echo "working directory: $WKDIR"
echo "data directory: $DATADIR"
echo -e "\n"

singularity run --cleanenv -B $DATADIR:/data -B $TMPDIR:/work -B $TMPDIR:/tmp -B $FSDIR:/fs \
    ${WKDIR}/images/fmriprep-21.0.2.simg \
    /data/ds000030/ \
    /data/preprocessed/ \
    participant --participant-label $SUB --work-dir /work/ --fs-license-file /fs/fs-license/license.txt --omp-nthreads 8 --nthreads 12 --mem-mb 30000 -vv --skip-bids-validation
