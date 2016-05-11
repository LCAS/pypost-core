import unittest
import numpy as np
from pypost.evaluator.ReturnKLEvaluator import ReturnKLEvaluator
from pypost.experiments.Trial import Trial


class testReturnKLEvaluator(unittest.TestCase):


    def setUp(self):
        self.evaluator = ReturnKLEvaluator()


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, ReturnKLEvaluator)

    def test_getEvaluation(self):
        data = None
        newData = None
        with self.assertRaises(RuntimeError):
            trial = Trial('/tmp', 0)
        with self.assertRaises(UnboundLocalError):
            self.evaluator.getEvaluation(data, newData, trial)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
