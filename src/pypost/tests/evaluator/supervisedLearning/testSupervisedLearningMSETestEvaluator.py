import unittest
from pypost.evaluator.supervisedLearning.SupervisedLearningMSETestEvaluator import SupervisedLearningMSETestEvaluator


class testSupervisedLearningMSETestEvaluator(unittest.TestCase):


    def setUp(self):
        self.evaluator = SupervisedLearningMSETestEvaluator()


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, SupervisedLearningMSETestEvaluator)

    def test_getEvaluation(self):
        with self.assertRaises(NameError):
            self.evaluator.getEvaluation(None, None, None)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
