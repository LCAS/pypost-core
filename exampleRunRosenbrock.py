#!/usr/bin/python

import os
import sys
import shutil

from rlt.experiments.Experiment import Experiment
from rlt.experiments.ExperimentFromScript import ExperimentFromScript
from rlt.examples.stochasticSearch.rosenbrock.Power_Rosenbrock import PowerRosenbrock

def runRosenbrock(numTrials):
    # Create directories if non-existent
    if not os.path.isdir('/tmp/testCategory'):
        os.mkdir('/tmp/testCategory')
        if not os.path.isdir('/tmp/testCategory/PowerRosenbrock'):
            os.mkdir('/tmp/testCategory/PowerRosenbrock')

    experiment = ExperimentFromScript('/tmp', 'testCategory', PowerRosenbrock)
    experiment.create()

    # FIXME: Find out what these parameters actually mean and fix
    # them
    evaluation = experiment.addEvaluation(['maxSizeReferenceStat'], [300], numTrials)

    experiment.startLocal()
    # TODO: Add fancy plotting

if __name__ == '__main__':
    runRosenbrock(4)
