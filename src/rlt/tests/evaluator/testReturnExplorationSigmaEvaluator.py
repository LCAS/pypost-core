import unittest
from rlt.tests import DataUtil
from rlt.evaluator.ReturnExplorationSigmaEvaluator import ReturnExplorationSigmaEvaluator
from rlt.data.Data import Data
from rlt.data.DataStructure import DataStructure
from rlt.data.DataManager import DataManager
from rlt.experiments.Trial import Trial


class testReturnExplorationSigmaEvaluator(unittest.TestCase):


    def setUp(self):
        self.evaluator = ReturnExplorationSigmaEvaluator()


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, ReturnExplorationSigmaEvaluator)

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
