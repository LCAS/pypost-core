#!/bin/bash

# Job name
#SBATCH -J §§experimentName§§
#SBATCH --array [1-§§numJobs§§]%§§numParallelJobs§§


# logfiles
#SBATCH -o §§experimentPath§§/out_%A_%a.log
#SBATCH -e §§experimentPath§§/err_%A_%a.log

# request computation time hh:mm
#SBATCH -t §§computationTime§§

# request virtual memory in MB
#SBATCH --mem-per-cpu=§§memory§§

#SBATCH -n 1


cd ~/policysearchtoolbox
module load matlab
module load gurobi
<<<<<<< HEAD
srun matlab -nosplash -nojvm -nodesktop -nodisplay -r "§§experimentCode§§; experiment.startCluster(§§clusterJobID§§,$SLURM_ARRAY_TASK_ID); exit;"
=======
srun matlab -nosplash -nojvm -nodesktop -nodisplay -r "§§experimentCode§§; experiment.startJobFromClusterID(§§clusterJobID§§,$SLURM_ARRAY_TASK_ID); exit;"
>>>>>>> a4db5bb58036a02e069522e0cfa0d27b36018d2b
