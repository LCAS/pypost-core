import unittest
import DataUtil
from evaluator.ReturnExplorationSigmaEvaluator import ReturnExplorationSigmaEvaluator
from data.Data import Data
from data.DataStructure import DataStructure
from data.DataManager import DataManager
from experiments.Trial import Trial


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