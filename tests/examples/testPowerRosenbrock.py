import numpy as np
import os
import unittest
from experiments.Experiment import Experiment
from experiments.ExperimentFromScript import ExperimentFromScript
from examples.stochasticSearch.rosenbrock.Power_Rosenbrock import PowerRosenbrock


class testPowerRosenbrock(unittest.TestCase):

    def testPowerRosenbrock(self):
        if not os.path.isdir('/tmp/testCategory'):
            os.mkdir('/tmp/testCategory')
            if not os.path.isdir('/tmp/testCategory/PowerRosenbrock'):
                os.mkdir('/tmp/testCategory/PowerRosenbrock')

        numTrials = 4
        experiment = ExperimentFromScript('/tmp', 'testCategory',
                                          PowerRosenbrock)
        experiment = Experiment.addToDataBase(experiment)

        evaluation = experiment.addEvaluation(['maxSizeReferenceStat'], [300],
                                              numTrials)

        experiment.startLocal()
