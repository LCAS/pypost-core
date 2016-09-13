import unittest
from pypost.envs import TransitionFunction
from pypost.sampler import EpisodeWithStepsSampler

class Test(unittest.TestCase):

    def setUp(self):
        self.sampler = EpisodeWithStepsSampler()
        self.dataManager = self.sampler.getEpisodeDataManager()

        self.tf = TransitionFunction(self.dataManager, 2, 1)

    # Test that sampler and data managers are set up correctly
    def test_init(self):

        stepManager = self.sampler.getEpisodeDataManager().subDataManager
        self.assertIn('states', stepManager.dataEntries)
        self.assertIn('actions', stepManager.dataEntries)
       # self.assertIn('nextStates', stepManager.dataEntries)

        stepSampler = self.sampler.stepSampler
        # check copy from nextStates to states
        #self.assertIn('nextStates', stepSampler._transitionElementOldStep)
        #self.assertIn('states', stepSampler._transitionElementNewStep)
       # self.assertEqual(len(stepSampler._transitionElementOldStep), 1)
       # self.assertEqual(len(stepSampler._transitionElementNewStep), 1)

