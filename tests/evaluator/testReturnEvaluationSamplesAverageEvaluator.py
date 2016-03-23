import unittest
from evaluator.ReturnEvaluationSamplesAverageEvaluator import ReturnEvaluationSamplesAverageEvaluator


class Test(unittest.TestCase):


    def setUp(self):
        self.evaluator = ReturnEvaluationSamplesAverageEvaluator(numSamplesEvaluation)


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, ReturnEvaluationSamplesAverageEvaluator)

    def test_getEvaluation(self):
        self.assertEqual(self.evaluator.getEvaluation())
        #TODO fix code


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()