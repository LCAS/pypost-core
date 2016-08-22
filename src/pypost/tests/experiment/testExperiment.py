import unittest
import os
import sys
import shutil
import numpy as np
from pypost.experiments.Experiment import Experiment
from pypost.experiments.Evaluation import Evaluation
from pypost.experiments.Trial import Trial
from pypost.experiments.Trial import TrialStoringType
from pypost.common.Settings import Settings
from pypost.examples.stochasticSearch.rosenbrock.Power_Rosenbrock import PowerRosenbrock

class TestTrial(Trial):

    def configure(self):
        pass

    def run(self):
        pass

class testExperiment(unittest.TestCase):

    def setUp(self):
        self.experiment = Experiment('/tmp', 'testCategory', PowerRosenbrock)
        self.experiment.deleteAllExperiments()
        self.experiment = Experiment('/tmp', 'testCategory', PowerRosenbrock)
        self.experiment.create()

    def tearDown(self):
        self.experiment.deleteExperiment()
        pass

    def testPath(self):
        self.assertEqual(self.experiment.path, '/tmp/testCategory/PowerRosenbrock')
        self.assertEqual(self.experiment.experimentPath, '/tmp/testCategory/PowerRosenbrock/experiment000')

    def testCreateOtherSettings(self):
        shutil.rmtree(self.experiment.experimentPath)
        print('Path exists:', os.path.exists(self.experiment.experimentPath))
        print(self.experiment.experimentPath)
        os.mkdir('/tmp/testCategory/PowerRosenbrock/dummy')
        os.mkdir('/tmp/testCategory/PowerRosenbrock/experiment001')
        settings = Settings("test")
        settings.registerProperty("dummy", 0)
        settings.store('/tmp/testCategory/PowerRosenbrock/experiment001/settings.yaml')
        self.experiment.create()
        self.assertEqual(len(os.listdir('/tmp/testCategory/PowerRosenbrock/dummy')), 0)
        os.rmdir('/tmp/testCategory/PowerRosenbrock/dummy')
        shutil.rmtree('/tmp/testCategory/PowerRosenbrock/experiment001')

    def testCreateTwice(self):
        self.experiment.create()
        self.assertEqual(self.experiment.experimentId, 0)

    def testAddEvaluation(self):
        eval = self.experiment.addEvaluation(['testParameter'], [100], 10)
        self.assertEqual(eval.numTrials, 10)
        self.assertEqual(self.experiment.getNumTrials(), 10)
        self.assertEqual(len(self.experiment.getTrialIDs()), 10)
        self.assertTrue(os.path.exists('/tmp/testCategory/PowerRosenbrock/experiment000/eval000'))
        for i in range(0, 10):
            self.assertTrue(os.path.exists('/tmp/testCategory/PowerRosenbrock/experiment000/eval000/trial%03i' % i))
        self.assertRaises(RuntimeError, self.experiment.addEvaluation, ['foo'], ['foo', 'bar'], 3)

    def testAddEvaluationDirectoryExists(self):
        os.mkdir('/tmp/testCategory/PowerRosenbrock/experiment000/eval000/')
        os.mkdir('/tmp/testCategory/PowerRosenbrock/experiment000/eval000/trial000')
        eval = self.experiment.addEvaluation(['testParameter'], [100], 10)

    def testAddEvaluationCollection(self):
        evals = self.experiment.addEvaluationCollection(['testParameter'], [0, 1], 10)
        self.assertEqual(len(evals), 2)

    def testLoadTrial(self):
        eval = self.experiment.addEvaluation(['testParameter'], [100], 10)
        trial = self.experiment.loadTrialFromID(0)
        self.assertEqual(trial.index, 0)
        self.assertEqual(trial.trialDir, '/tmp/testCategory/PowerRosenbrock/experiment000/eval000/trial000')
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
        trial.store('a', 5, TrialStoringType.STORE_PER_ITERATION)
        trial.store('a', 10, TrialStoringType.STORE_PER_ITERATION)
        self.assertIn('a', trial.storePerIteration)
        self.assertEqual(trial.getProperty('a'), 10)
        trial.store('b', 12, TrialStoringType.ACCUMULATE_PER_ITERATION)
        trial.store('b', [14], TrialStoringType.ACCUMULATE_PER_ITERATION)
        self.assertTrue((trial.getProperty('b') == np.array([[12], [14]])).all())
        trial.store('c', 4, TrialStoringType.STORE)
        trial.store('c', 9, TrialStoringType.STORE)
        self.assertIn('c', trial.storePerTrial)
        self.assertEqual(trial.getProperty('c'), 9)

    def testEvaluationPowerRosenbrock(self):
        if not os.path.isdir('/tmp/testExperiment'):
            os.mkdir('/tmp/testExperiment')
            if not os.path.isdir('/tmp/testExperiment/PowerRosenbrock'):
                os.mkdir('/tmp/testExperiment/PowerRosenbrock')
        numTrials = 2

        Experiment('/tmp', 'testCategory', PowerRosenbrock)
        self.experiment.create()
        evaluation2 = self.experiment.addEvaluationCollection(['numParameters'], [2, 4, 6], numTrials)
        evaluation1 = self.experiment.addEvaluationCollection(['numSamplesEpisodes'], [10, 20], numTrials)

        self.assertEqual(len(self.experiment.evaluations), 4)

    def testReload(self):
            if not os.path.isdir('/tmp/testExperiment'):
                os.mkdir('/tmp/testExperiment')
                if not os.path.isdir('/tmp/testExperiment/PowerRosenbrock'):
                    os.mkdir('/tmp/testExperiment/PowerRosenbrock')
            numTrials = 2
            # FIXME: Find out what these parameters actually mean and fix
            # them
            evaluation2 = self.experiment.addEvaluationCollection(['numParameters'], [2, 4, 6], numTrials)
            evaluation1 = self.experiment.addEvaluationCollection(['numSamplesEpisodes'], [10, 20], numTrials)

            self.experiment.startLocal()
            self.assertEqual(len(self.experiment.evaluations), 4)



if __name__ == '__main__':
    unittest.main()
