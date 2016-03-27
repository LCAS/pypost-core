import unittest
from experiments.Experiment import Experiment
from experiments.Evaluation import Evaluation


class testEvaluation(unittest.TestCase):

    def testSetExperiment(self):
        testExperiment = Experiment('/tmp/', "test", "test")
        evaluation = Evaluation(testExperiment, 0, None, None, None)
