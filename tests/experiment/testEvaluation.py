import unittest
import sys
sys.path.append('../src/')
from experiments.Experiment import Experiment
from experiments.Evaluation import Evaluation


class testEvaluation(unittest.TestCase):
    
    def testSetExperiment(self):
        testExperiment = Experiment("test", "test")
        evaluation = Evaluation(testExperiment, 0, None, None, None)
        
        # Not sure how to test this shit