import unittest
import os
import sys
import shutil
import numpy as np
from pypost.experiments.Experiment import Experiment
from pypost.experiments.ExperimentFromScript import ExperimentFromScript
from pypost.experiments.Evaluation import Evaluation
from pypost.experiments.Trial import Trial
from pypost.experiments.Trial import StoringType
from pypost.common.Settings import Settings

class TestTrial(Trial):

    def configure(self):
        pass

    def run(self):
        pass

class testExperiment(unittest.TestCase):

    def setUp(self):
        self.experiment = ExperimentFromScript('/tmp', 'testCategory', TestTrial)
        self.experiment.create()

    def tearDown(self):
        self.experiment.deleteExperiment()
        pass

    def testPath(self):
        self.assertEqual(self.experiment.path, '/tmp/testCategory/TestTrial')
        self.assertEqual(self.experiment.experimentPath, '/tmp/testCategory/TestTrial/experiment000')

    def testCreateOtherSettings(self):
        shutil.rmtree(self.experiment.experimentPath)
        print('Path exists:', os.path.exists(self.experiment.experimentPath))
        print(self.experiment.experimentPath)
        os.mkdir('/tmp/testCategory/TestTrial/dummy')
        os.mkdir('/tmp/testCategory/TestTrial/experiment001')
        settings = Settings("test")
        settings.registerProperty("dummy", 0)
        settings.store('/tmp/testCategory/TestTrial/experiment001/settings.yaml')
        self.experiment.create()
        self.assertEqual(len(os.listdir('/tmp/testCategory/TestTrial/dummy')), 0)
        os.rmdir('/tmp/testCategory/TestTrial/dummy')
        shutil.rmtree('/tmp/testCategory/TestTrial/experiment001')

    def testCreateTwice(self):
        self.experiment.create()
        self.assertEqual(self.experiment.experimentId, 0)

    def testAddEvaluation(self):
        eval = self.experiment.addEvaluation(['testParameter'], [100], 10)
        self.assertEqual(eval.numTrials, 10)
        self.assertEqual(self.experiment.getNumTrials(), 10)
        self.assertEqual(len(self.experiment.getTrialIDs()), 10)
        self.assertTrue(os.path.exists('/tmp/testCategory/TestTrial/experiment000/eval000'))
        for i in range(0, 10):
            self.assertTrue(os.path.exists('/tmp/testCategory/TestTrial/experiment000/eval000/trial%03i' % i))
        self.assertRaises(RuntimeError, self.experiment.addEvaluation, ['foo'], ['foo', 'bar'], 3)

    def testAddEvaluationDirectoryExists(self):
        os.mkdir('/tmp/testCategory/TestTrial/experiment000/eval000/')
        os.mkdir('/tmp/testCategory/TestTrial/experiment000/eval000/trial000')
        eval = self.experiment.addEvaluation(['testParameter'], [100], 10)

    def testAddEvaluationCollection(self):
        evals = self.experiment.addEvaluationCollection(['testParameter'], [0, 1], 10)
        self.assertEqual(len(evals), 2)

    def testLoadTrial(self):
        eval = self.experiment.addEvaluation(['testParameter'], [100], 10)
        trial = self.experiment.loadTrialFromID(0)
        self.assertEqual(trial.index, 0)
        self.assertEqual(trial.trialDir, '/tmp/testCategory/TestTrial/experiment000/eval000/trial000')
        self.assertRaises(KeyError, self.experiment.loadTrialFromID, 234)

    def testStart(self):
        e = self.experiment
        e.startDefaultTrial()

    def testGetEvaluation(self):
        eval = self.experiment.addEvaluation(['testParameter'], [100], 10)
        e2 = self.experiment.getEvaluation(0)
        self.assertEqual(eval, e2)

    def testGetEvaluationIndex(self):
        eval1 = self.experiment.addEvaluation(['testParameter'], [100], 10)
        eval2 = self.experiment.addEvaluation(['testParameter2'], [100], 10)
        eval3 = Evaluation(self.experiment, 14, eval1.settings, ['foo'], ['bar'], 10)
        index = self.experiment.getEvaluationIndex(eval1)
        index2 = self.experiment.getEvaluationIndex(eval2)
        index3 = self.experiment.getEvaluationIndex(eval3)
        self.assertEqual(index, 0)
        self.assertEqual(index2, 1)
        self.assertEqual(index3, None)

    def testStartLocal(self):
        eval = self.experiment.addEvaluation(['testParameter'], [100], 10)
        self.experiment.startLocal()

    def testSetDefaultParameter(self):
        self.experiment.setDefaultParameter('parameter1', 14)
        self.assertEqual(self.experiment.defaultSettings.getProperty('parameter1'), 14)
        self.experiment.setDefaultParameter('settings.parameter1', 18)
        self.assertEqual(self.experiment.defaultSettings.getProperty('parameter1'), 18)

    def testTrialStore(self):
        trial = self.experiment.defaultTrial
        trial.store('a', 5, StoringType.STORE_PER_ITERATION)
        trial.store('a', 10, StoringType.STORE_PER_ITERATION)
        self.assertIn('a', trial.storePerIteration)
        self.assertEqual(trial.getProperty('a'), 10)
        trial.store('b', 12, StoringType.ACCUMULATE_PER_ITERATION)
        trial.store('b', [14], StoringType.ACCUMULATE_PER_ITERATION)
        self.assertTrue((trial.getProperty('b') == np.array([[12], [14]])).all())
        trial.store('c', 4, StoringType.STORE)
        trial.store('c', 9, StoringType.STORE)
        self.assertIn('c', trial.storePerTrial)
        self.assertEqual(trial.getProperty('c'), 9)

if __name__ == '__main__':
    unittest.main()
