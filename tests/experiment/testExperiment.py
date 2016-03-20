import unittest
import os
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
        self.assertEqual(self.experiment.experimentPath, "Experiments/data/testCategory/TestTrial")
        
    def testFfjksdhjkfhsduzh(self):
        e = self.experiment
        e.startDefaultTrial()
        
        
if __name__ == '__main__':
    unittest.main()
        