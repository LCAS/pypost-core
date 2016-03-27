import unittest
from evaluator.WindowPredictionEvaluator import WindowPredictionEvaluator


class testWindowPredictionEvaluator(unittest.TestCase):


    def setUp(self):
        self.evaluator = WindowPredictionEvaluator()


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.evaluator, WindowPredictionEvaluator)

    def test_getEvaluation(self):
        with self.assertRaises(NotImplementedError):
            self.evaluator.getEvaluation(None, None, None)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()