import numpy as np
import unittest
from data.DataManipulator import DataManipulator
from environments.EpisodicContextualLearningTask import \
EpisodicContextualLearningTask
from sampler.EpisodeSampler import EpisodeSampler


class testEpisodicContextualLearningTask(unittest.TestCase):
    def test_sampleContext(self):
        s = EpisodeSampler()
        e = EpisodicContextualLearningTask(s, 10)

        e.sampleInitContextFunc = 2
        self.assertRaises(ValueError, e.sampleContext, 10)

        e.sampleInitContextFunc = 0
        self.assertEqual(e.sampleContext(10).shape, (10, 10))

        e.sampleInitContextFunc = 1
        e.dimState = 1
        self.assertEqual(e.sampleContext(10).shape, (10, 10))

        s2 = EpisodeSampler()
        e2 = EpisodicContextualLearningTask(s2, 0)
        self.assertTrue((e2.sampleContext(10) == np.zeros((10, 0))).all())


    def sampleStatesUniform(self):
        pass

    def sampleStatesGaussian(self):
        pass
