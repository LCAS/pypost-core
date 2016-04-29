import unittest
from rlt.environments.EpisodicContextualParameterLearningTask import \
EpisodicContextualParameterLearningTask
from rlt.sampler.EpisodeSampler import EpisodeSampler



class testEpisodicContextualParameterLearningTask(unittest.TestCase):

    def test_init(self):
        sampler = EpisodeSampler()
        t = EpisodicContextualParameterLearningTask(sampler, 15, 15)

        self.assertEqual(t.dataManager.dataEntries['parameters'].numDimensions,
                         15)
        self.assertEqual(t.dimParameters,
                         15)
        self.assertTrue((t.minRangeParameters ==
                         sampler.dataManager.getMinRange('parameters')).all())
        self.assertTrue((t.maxRangeParameters ==
                         sampler.dataManager.getMaxRange('parameters')).all())

    def test_sampleReturn(self):
        sampler = EpisodeSampler()
        t = EpisodicContextualParameterLearningTask(sampler, 15, 15)
        self.assertRaises(NotImplementedError, t.sampleReturn)
