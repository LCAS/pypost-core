import unittest
from pypost.sampler import EpisodeWithStepsSampler, NumStepsTerminationFunction
from pypost.envs import MountainCar
from pypost.common import SettingsManager

class Test(unittest.TestCase):

    # Test that sampler and data managers are set up correctly
    def setUp(self):

        defaultSettings = SettingsManager.getDefaultSettings()
        defaultSettings.setProperty('numTimeSteps', 20)

        self.sampler = EpisodeWithStepsSampler(samplerNameSteps='steps')
        self.sampler.numSamples = 3
        self.dataManager = self.sampler.getEpisodeDataManager()
        self.sampler.stepSampler.setTerminationFunction(NumStepsTerminationFunction(
            self.dataManager, None, numTimeSteps=20))
        environment = MountainCar(self.dataManager)

        self.sampler.setContextSampler(environment.sampleContext)
        self.sampler.setActionPolicy(environment.sampleAction)
        self.sampler.setTransitionFunction(environment.transitionFunction)
        self.sampler.setRewardFunction(environment.sampleReward)
        self.sampler.setInitStateSampler(environment.sampleInitState)

    def test_sampleData(self):
        self.sampler.setParallelSampling(True)
        newData = self.dataManager.createDataObject([3, 20])
        self.sampler >> newData[...]
        print('States:', newData[1, :].states)
        print('NextStates:', newData[1, :].nextStates)
        #print('Actions:', newData[...].actions)
        #print('Rewards:', newData[...].rewards)
        #states = newData.getDataEntry('states')
        #self.assertTrue(states.shape == (6000, 2))
        #upper_state_limit = 0.6 # may be changed in mountainCar simulator
        #self.assertTrue(np.max(states[:, 1]) <= upper_state_limit)