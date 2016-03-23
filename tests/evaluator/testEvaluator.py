import unittest
from evaluator.Evaluator import Evaluator
from evaluator.LogType import LogType


class testEvaluator(unittest.TestCase):


    def setUp(self):
        self.evaluator = Evaluator('testEvaluator')


    def tearDown(self):
        pass


    def test_init(self):
        self.assertEqual(self.evaluator.name, 'testEvaluator')

    def test_publish(self):
        self.evaluator.publish('Testmessage1. Success!')
        self.evaluator.publish('Testmessage2. Success!', LogType.EVALUATION)

    def test_getEvaluation():
        with self.assertRaises():
            self.evaluator.getEvaluation()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()