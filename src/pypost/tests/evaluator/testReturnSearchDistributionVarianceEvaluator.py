import unittest
from pypost.experiments.Trial import Trial
from pypost.evaluator.ReturnSearchDistributionVarianceEvaluator import ReturnSearchDistributionVarianceEvaluator


class testReturnSearchDistributionMeanEvaluator(unittest.TestCase):


    def setUp(self):
        self.evaluator = ReturnSearchDistributionVarianceEvaluator()


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, ReturnSearchDistributionVarianceEvaluator)

    def test_getEvaluation(self):
        data = None
        newData = None
        # trial = GaussianLinearInFeatures(DataManager('testmngr'), outputVariables[0], inputVariables, functionName, featureGenerator, doInitWeights)
        with self.assertRaises(RuntimeError):
            trial = Trial('/tmp', 0)
        with self.assertRaises(UnboundLocalError):
            self.evaluator.getEvaluation(data, newData, trial)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
