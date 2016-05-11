import unittest
from pypost.evaluator.supervisedLearning.SupervisedLearningMSETrainEvaluator import SupervisedLearningMSETrainEvaluator
from pypost.data.Data import Data
from pypost.data.DataManager import DataManager
from pypost.data.DataStructure import DataStructure


class testSupervisedLearningMSETrainEvaluator(unittest.TestCase):


    def setUp(self):
        self.evaluator = SupervisedLearningMSETrainEvaluator()


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, SupervisedLearningMSETrainEvaluator)

    def test_getEvaluationData(self):
        data = Data(DataManager('testmngr'), DataStructure(1))
        self.assertIs(self.evaluator.getEvaluationData(data, None), data)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
