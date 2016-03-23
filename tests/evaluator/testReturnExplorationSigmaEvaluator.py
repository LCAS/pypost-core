import unittest
import DataUtil
from evaluator.ReturnExplorationSigmaEvaluator import ReturnExplorationSigmaEvaluator
from data.Data import Data
from data.DataStructure import DataStructure
from data.DataManager import DataManager


class Test(unittest.TestCase):


    def setUp(self):
        self.evaluator = ReturnExplorationSigmaEvaluator()


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, ReturnExplorationSigmaEvaluator)

    def test_getEvaluation(self):
        data = Data(DataManager('testmngr1'), DataStructure(3))
        testmngr = DataUtil.createTestManager()
        newData = Data(testmngr, DataStructure(3))
        print(self.evaluator.getEvaluation(data, newData, trial))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()