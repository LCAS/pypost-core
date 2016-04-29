import unittest
from rlt.sampler.Sampler import Sampler
from rlt.data.DataManager import DataManager
from rlt.evaluator.ReturnDecisionStagesEvaluator import ReturnDecisionStagesEvaluator


class testReturnDecisionStagesEvaluator(unittest.TestCase):


    def setUp(self):
        sampler = Sampler(DataManager('testmngr'), 'testSampler')
        self.evaluator = ReturnDecisionStagesEvaluator(sampler)


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, ReturnDecisionStagesEvaluator)
        self.assertEqual(self.evaluator.numSamplesEvaluation, 100)
        self.assertEqual(self.evaluator.numStepsEvaluation, 50)

    def test_getEvaluation(self):
        with self.assertRaises(AttributeError):
            self.evaluator.getEvaluation(None, None, None)
        #TODO fix buggy code

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
