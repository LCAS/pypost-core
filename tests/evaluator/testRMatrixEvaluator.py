import unittest
from evaluator.RMatrixEvaluator import RMatrixEvaluator


class Test(unittest.TestCase):


    def setUp(self):
        self.evaluator = RMatrixEvaluator()


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, RMatrixEvaluator)

    def test_getEvaluation(self):
        #TODO trial.learner.Raa??


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()