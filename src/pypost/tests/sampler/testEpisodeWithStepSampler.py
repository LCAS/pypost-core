import unittest

import numpy as np

from pypost.common import SettingsManager
from pypost.data import DataManipulator
from pypost.mappings import Mapping
from pypost.sampler import EpisodeWithStepsSampler
from pypost.tests import DataUtil


class TestEnvironment(Mapping):

    def __init__(self, dataManager, inputVariables = ['states', 'actions'], outputVariables = ['nextStates']):
        Mapping.__init__(self, dataManager, inputVariables, outputVariables)

    @Mapping.MappingMethod()
    def transitionFunction(self, states, actions):
        return states + 1

    @DataManipulator.DataMethod(inputArguments=[], outputArguments=['states'])
    def initState(self, numElements):
        return np.ones((numElements,1))

    @DataManipulator.DataMethod(inputArguments=['contexts'], outputArguments=['states'])
    def initStateFromContext(self, contexts):
        return np.sum(contexts, axis=1)

    @DataManipulator.DataMethod(inputArguments=[], outputArguments=['contexts'])
    def initContexts(self, numElements):
        return np.ones((numElements, 1)) * 0.5

class TestPolicy(Mapping):
    mappingFunctionName = 'getAction'

    def __init__(self, dataManager):
        Mapping.__init__(self, dataManager, ['states'], ['actions'])

    @Mapping.MappingMethod()
    def getAction(self, states):
        return states * 2

class TestReward(Mapping):
    mappingFunctionName = 'getReward'

    def __init__(self, dataManager):
        Mapping.__init__(self, dataManager, ['states', 'actions'], ['rewards'])

    @Mapping.MappingMethod()
    def getReward(self, states, actions):
        return states * 2

class testStepSampler(unittest.TestCase):


    def setUp(self):
        settings = SettingsManager.getDefaultSettings()
        settings.setProperty('numTimeSteps', 40)
        self.dataManager = DataUtil.createTestManagerSteps()
        self.stepSamplerEpisodes = EpisodeWithStepsSampler(self.dataManager, 'episodes', 'steps')

        #Todo: get function for data manager
    def tearDown(self):
        pass


    def testSampling(self):
        environment = TestEnvironment(self.dataManager)
        policy = TestPolicy(self.dataManager)
        reward = TestReward(self.dataManager)

        self.stepSamplerEpisodes.setInitStateSampler(environment.initState)
        self.stepSamplerEpisodes.setTransitionFunction(environment)
        self.stepSamplerEpisodes.setActionPolicy(policy)
        self.stepSamplerEpisodes.setRewardFunction(reward)

        data = self.dataManager.createDataObject([10, 100])
        data[Ellipsis] >> self.stepSamplerEpisodes

        states = data.getDataEntry('states', 1)
        actions = data.getDataEntry('actions', 2)
        rewards = data.getDataEntry('rewards', 3)

        statesTarget = np.array(range(1, 41))
        self.assertTrue((abs(states.transpose() - statesTarget) < 0.00001).all())
        self.assertTrue((abs(states * 2 - actions) < 0.00001).all())
        self.assertTrue((abs(states * 2 - rewards) < 0.00001).all())


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']

    unittest.main()

