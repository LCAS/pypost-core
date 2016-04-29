import unittest
from rlt.evaluator.supervisedLearning.SupervisedLearningMSETrainEvaluator import SupervisedLearningMSETrainEvaluator
from rlt.data.Data import Data
from rlt.data.DataManager import DataManager
from rlt.data.DataStructure import DataStructure


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
