#!/usr/bin/python

import os
import sys
import shutil
sys.path.append(
    os.path.abspath(os.path.dirname(os.path.realpath(__file__))+'/src/'))

from experiments.Experiment import Experiment
from experiments.ExperimentFromScript import ExperimentFromScript
from examples.stochasticSearch.rosenbrock.NES_rosenbrock import NESRosenbrock

def runRosenbrock(numTrials):
    # Create directories if non-existent
    if not os.path.isdir('/tmp/testCategory'):
        os.mkdir('/tmp/testCategory')
        if not os.path.isdir('/tmp/testCategory/NESRosenbrock'):
            os.mkdir('/tmp/testCategory/NESRosenbrock')

    experiment = ExperimentFromScript('/tmp', 'testCategory', NESRosenbrock)
    experiment.create()

    # FIXME: Find out what these parameters actually mean and fix
    # them
    evaluation = experiment.addEvaluation(['maxSizeReferenceStat'], [300], numTrials)

    experiment.startLocal()
    # TODO: Add fancy plotting

if __name__ == '__main__':
    runRosenbrock(4)
