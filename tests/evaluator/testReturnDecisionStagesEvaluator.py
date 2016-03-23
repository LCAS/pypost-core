import unittest
from evaluator.ReturnDecisionStagesEvaluator import ReturnDecisionStagesEvaluator
from sampler.Sampler import Sampler
import DataUtil


class Test(unittest.TestCase):


    def setUp(self):
        datamngr = DataUtil.createTestManager()
        sampler = Sampler(dataManager, samplerName)
        self.evaluator = ReturnDecisionStagesEvaluator(sampler)


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, ReturnDecisionStagesEvaluator)
        self.assertEqual(self.evaluator.numSamplesEvaluation, 100)
        self.assertEqual(self.sampler.numStepsEvaluation, 50)

    def test_getEvaluation(self):
        self.sampler.getEvaluation()
        #TODO fix buggy code

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()