'''
Created on 20.03.2016

@author: Sebastian Kreutzer
'''
import os
import sys
sys.path.append(
    os.path.abspath(os.path.dirname(os.path.realpath(__file__))+'/../../../'))

from experiments.Experiment import Experiment
from experiments.ExperimentFromScript import ExperimentFromScript
from examples.stochasticSearch.rosenbrock.Power_Rosenbrock import PowerRosenbrock

if __name__ == '__main__':
    # Create directories if non-existent
    if not os.path.isdir('/tmp/testCategory'):
        os.mkdir('/tmp/testCategory')
        if not os.path.isdir('/tmp/testCategory/PowerRosenbrock'):
            os.mkdir('/tmp/testCategory/PowerRosenbrock')

    numTrials = 4
    experiment = ExperimentFromScript('/tmp', 'testCategory', PowerRosenbrock)
    experiment = Experiment.addToDataBase(experiment)

    print(experiment)

    # FIXME(Sebastian): Find out what these parameters actually mean
    evaluation = experiment.addEvaluation(None, None, numTrials)

    experiment.startLocal()

    # TODO(Sebastian): Add fancy plotting and shit
