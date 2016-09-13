import unittest
from pypost.experiments import Experiment
from pypost.examples.stochasticSearch.rosenbrock.Power_Rosenbrock import PowerRosenbrock


class testPowerRosenbrock(unittest.TestCase):

    def testPowerRosenbrock(self):


        numTrials = 4
        experiment = Experiment('/tmp', 'testCategory', PowerRosenbrock)
        experiment.create()

        evaluation = experiment.addEvaluation(['maxSizeReferenceStat'], [300],
                                              numTrials)

        experiment.startLocal()

        experiment.defaultTrial.configured = False
        with self.assertRaises(RuntimeError):
            experiment.defaultTrial.run()
