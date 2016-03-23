import unittest
import os
import sys
sys.path.append(
    os.path.abspath(os.path.dirname(os.path.realpath(__file__))+'/../../src'))
from experiments.Experiment import Experiment
from experiments.ExperimentFromScript import ExperimentFromScript
from experiments.Evaluation import Evaluation
from experiments.Trial import Trial

class TestTrial(Trial):

    def configure(self):
        print("Kill me")

    def run(self):
        print("Please")

class testExperiment(unittest.TestCase):

    def setUp(self):
        self.experiment = ExperimentFromScript('/tmp', 'testCategory', TestTrial)
        Experiment.addToDataBase(self.experiment)

    def tearDown(self):
        self.experiment.deleteExperiment()

    def testPath(self):
        self.assertEqual(self.experiment.path, '/tmp/testCategory/TestTrial')
        self.assertEqual(self.experiment.experimentPath, '/tmp/testCategory/TestTrial/settings000')

    def testLoadTrial(self):
        pass

    def testFfjksdhjkfhsduzh(self):
        e = self.experiment
        e.startDefaultTrial()


if __name__ == '__main__':
    unittest.main()
