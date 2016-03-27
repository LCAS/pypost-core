import unittest
import DataUtil
import numpy as np
from evaluator.ReturnMaxEvaluator import ReturnMaxEvaluator
from data.Data import Data
from data.DataStructure import DataStructure


class testReturnMaxEvaluator(unittest.TestCase):

    def setUp(self):
        self.evaluator = ReturnMaxEvaluator()

    def tearDown(self):
        pass

    def test_init(self):
        self.assertIsInstance(self.evaluator, ReturnMaxEvaluator)

    def test_getEvaluation(self):
        data = None
        testmng = DataUtil.createTestManager2()
        newData = testmng.getDataObject([5,3,2])
        a = np.array([[52,36], [12,42], [14,10], [90, 5], [33, 20]])
        newData.setDataEntry('returns', [], a)
        trial = None
        self.assertEqual(self.evaluator.getEvaluation(data, newData, trial), 90)
        a = np.array([[12,93], [92,55], [90,12], [34, 39], [12, 12]])
        newData.setDataEntry('returns', [], a)
        self.assertEqual(self.evaluator.getEvaluation(data, newData, trial), 93)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()