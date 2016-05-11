import unittest
from pypost.evaluator.supervisedLearning.SupervisedLearningMSEEvaluator import SupervisedLearningMSEEvaluator


class testSupervisedLearningMSEEvaluator(unittest.TestCase):


    def setUp(self):
        self.evaluator = SupervisedLearningMSEEvaluator()


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, SupervisedLearningMSEEvaluator)

    def test_getEvaluation(self):
        with self.assertRaises(NotImplementedError):
            self.evaluator.getEvaluation(None, None, None)

    def test_getEvaluationData(self):
        with self.assertRaises(NotImplementedError):
            self.evaluator.getEvaluationData(None, None)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
