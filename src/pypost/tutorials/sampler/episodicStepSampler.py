import numpy as np

from pypost.sampler import EpisodeWithStepsSampler
from pypost.data import DataManipulator
from pypost.mappings import Mapping
'''
In this tutorial, we will learn how to create samples
'''

class TestEnvironment(Mapping):

    def __init__(self, dataManager, inputVariables = ['states', 'actions'], outputVariables = ['nextStates']):
        subDataManager = dataManager.subDataManager

        dataManager.addDataEntry('contexts', 3)
        subDataManager.addDataEntry('states', 2)
        subDataManager.addDataEntry('actions', 2)
        subDataManager.addDataEntry('rewards', 1)

        Mapping.__init__(self, dataManager, inputVariables, outputVariables)

    @Mapping.MappingMethod()
    def transitionFunction(self, states, actions):
        return states + 1

    @DataManipulator.DataMethod(inputArguments=[], outputArguments=['states'])
    def initState(self, numElements):
        return np.ones((numElements,2))

    @DataManipulator.DataMethod(inputArguments=['contexts'], outputArguments=['states'])
    def initStateFromContext(self, contexts):
        return np.sum(contexts, axis=1) * np.ones(2)

    @DataManipulator.DataMethod(inputArguments=[], outputArguments=['contexts'])
    def initContexts(self, numElements):
        return np.ones((numElements, 1)) * 0.5

class TestPolicy(Mapping):

    def __init__(self, dataManager):
        Mapping.__init__(self, dataManager, ['states'], ['actions'])

    @Mapping.MappingMethod()
    def getAction(self, states):
        return states * 2 * np.ones(2)

class TestReward(Mapping):

    def __init__(self, dataManager):
        Mapping.__init__(self, dataManager, ['states', 'actions'], ['rewards'])

    @Mapping.MappingMethod()
    def getReward(self, states, actions):
        return states[:,0:1] * 2


sampler = EpisodeWithStepsSampler()
dataManager = sampler.getEpisodeDataManager()

environment = TestEnvironment(dataManager)
policy = TestPolicy(dataManager)
reward = TestReward(dataManager)

sampler.setInitStateSampler(environment.initState)
sampler.setTransitionFunction(environment)
sampler.setActionPolicy(policy)
sampler.setRewardFunction(reward)

data = dataManager.createDataObject([1, 20])

data[...] >> sampler

states = data.getDataEntry('states', 1)
actions = data.getDataEntry('actions', 2)
rewards = data.getDataEntry('rewards', 3)

print('States:', data[...].states)
print('Actions:', data[...].actions)
print('Rewards:', data[...].rewards)

