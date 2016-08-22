#!/usr/bin/python

import os
import sys
import shutil

from pypost.experiments.Experiment import Experiment
from pypost.examples.stochasticSearch.rosenbrock.Power_Rosenbrock import PowerRosenbrock

def runRosenbrock(numTrials):
    # Create directories if non-existent

    experiment = Experiment('/tmp', 'testCategory', PowerRosenbrock)
    experiment.create()

    # FIXME: Find out what these parameters actually mean and fix
    # them
    evaluation2 = experiment.addEvaluationCollection(['numParameters'], [2, 4, 6], numTrials)
    evaluation1 = experiment.addEvaluationCollection(['numSamplesEpisodes'], [10, 20], numTrials)

    evaluationsQuery = experiment.getEvaluationsFromQuery({'numParameters': 2})
    experiment.startLocal()
    # TODO: Add fancy plotting

if __name__ == '__main__':

    runRosenbrock(2)

