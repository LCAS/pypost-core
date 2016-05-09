import numpy as np
import os
import unittest
from rlt.experiments.Experiment import Experiment
from rlt.experiments.ExperimentFromScript import ExperimentFromScript
from rlt.examples.stochasticSearch.rosenbrock.Power_Rosenbrock import PowerRosenbrock


class testPowerRosenbrock(unittest.TestCase):

    def testPowerRosenbrock(self):

        if not os.path.isdir('/tmp/testCategory'):
            os.mkdir('/tmp/testCategory')
            if not os.path.isdir('/tmp/testCategory/PowerRosenbrock'):
                os.mkdir('/tmp/testCategory/PowerRosenbrock')

        numTrials = 4
        experiment = ExperimentFromScript('/tmp', 'testCategory',
                                          PowerRosenbrock)
        experiment.create()

        evaluation = experiment.addEvaluation(['maxSizeReferenceStat'], [300],
                                              numTrials)

        experiment.startLocal()

        experiment.defaultTrial.configured = False
        with self.assertRaises(RuntimeError):
            experiment.defaultTrial.run()
