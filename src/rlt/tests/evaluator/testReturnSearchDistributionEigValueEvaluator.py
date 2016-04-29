import unittest
from rlt.evaluator.ReturnSearchDistributionEigValueEvaluator import ReturnSearchDistributionEigValueEvaluator
from rlt.experiments.Trial import Trial


class testReturnSearchDistributionEigValueEvaluator(unittest.TestCase):


    def setUp(self):
        self.evaluator = ReturnSearchDistributionEigValueEvaluator()


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, ReturnSearchDistributionEigValueEvaluator)

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
