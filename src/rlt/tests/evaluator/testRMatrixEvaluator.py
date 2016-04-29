import unittest
from rlt.evaluator.RMatrixEvaluator import RMatrixEvaluator
from rlt.experiments.Trial import Trial


class testRMatrixEvaluator(unittest.TestCase):

    def setUp(self):
        self.evaluator = RMatrixEvaluator()

    def tearDown(self):
        pass

    def test_init(self):
        self.assertIsInstance(self.evaluator, RMatrixEvaluator)

    def test_getEvaluation(self):
        data = None
        newData = None
        # trial = GaussianLinearInFeatures(DataManager('testmngr'), outputVariables[0], inputVariables, functionName, featureGenerator, doInitWeights)
        with self.assertRaises(RuntimeError):
            trial = Trial('/tmp', 0)
        with self.assertRaises(UnboundLocalError):
            self.evaluator.getEvaluation(data, newData, trial)


if __name__ == "__main__":
    unittest.main()
