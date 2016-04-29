import unittest
from rlt.evaluator.Evaluator import Evaluator
from rlt.evaluator.LogType import LogType
from rlt.experiments.Trial import StoringType


class testEvaluator(unittest.TestCase):
    def setUp(self):
        self.evaluator = Evaluator(
            'testEval', {'preLoop', 'endLoop'}, StoringType.ACCUMULATE)

    def tearDown(self):
        pass

    def test_init(self):
        self.assertEqual(self.evaluator.name, 'testEval')

    def test_publish(self):
        self.evaluator.publish('Testmessage1. Success!')
        self.evaluator.publish('Testmessage2. Success!', LogType.EVALUATION)

    def test_getEvaluation(self):
        with self.assertRaises(NotImplementedError):
            self.evaluator.getEvaluation(None, None, None)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
