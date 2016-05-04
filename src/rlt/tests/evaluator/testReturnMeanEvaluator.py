import unittest
from rlt.tests import DataUtil
import numpy as np
from rlt.evaluator.ReturnMeanEvaluator import ReturnMeanEvaluator


class testReturnMeanEvaluator(unittest.TestCase):


    def setUp(self):
        self.evaluator = ReturnMeanEvaluator()


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, ReturnMeanEvaluator)

    def test_getEvaluation(self):
        data = None
        testmng = DataUtil.createTestManager2()
        newData = testmng.getDataObject([5,3,2])
        a = np.array([[52,36], [12,42], [14,10], [90, 5], [33, 20]])
        newData.setDataEntry('returns', [], a)
        trial = None
        self.assertAlmostEqual(self.evaluator.getEvaluation(data, newData, trial), 31.4, delta = 0.001)
        a = np.array([[12,93], [92,55], [90,12], [34, 39], [12, 12]])
        newData.setDataEntry('returns', [], a)
        self.assertAlmostEqual(self.evaluator.getEvaluation(data, newData, trial), 45.1, delta = 0.001)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
