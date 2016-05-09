import unittest
from rlt.evaluator.ReturnSearchDistributionMeanEvaluator \
import ReturnSearchDistributionMeanEvaluator
from rlt.experiments.Trial import Trial


class testReturnSearchDistributionMeanEvaluator(unittest.TestCase):


    def setUp(self):
        self.evaluator = ReturnSearchDistributionMeanEvaluator()


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, ReturnSearchDistributionMeanEvaluator)

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