import cProfile

import numpy as np

import pypost.tests.DataUtil as DataUtil
from pypost.data.DataManipulator import DataManipulator
from pypost.mappings.Mapping import Mapping
from pypost.sampler.StepSampler import StepSampler


class TestEnvironment(Mapping):

    def __init__(self, dataManager, inputVariables = ['states', 'actions'], outputVariables = ['nextStates']):
        Mapping.__init__(self, dataManager, inputVariables, outputVariables)

    @Mapping.MappingMethod()
    def transitionFunction(self, states, actions):
        return states + 1

    @DataManipulator.DataMethod(inputArguments=[], outputArguments=['states'])
    def initState(self, numElements):
        return np.ones((numElements,1))

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


        self.assertTrue( (abs(states.transpose() - statesTarget ) < 0.00001).all())
        self.assertTrue((abs(states * 2 - actions) < 0.00001).all())
        self.assertTrue((abs(states * 2- rewards) < 0.00001).all())


if __name__ == "__main__" or True:
    #import sys;sys.argv = ['', 'Test.testName']
    dataManager = DataUtil.createTestManagerSteps()
    sampler = StepSampler(dataManager, 'episodes')

    environment = TestEnvironment(dataManager)
    policy = TestPolicy(dataManager)
    reward = TestReward(dataManager)

    sampler.setInitStateSampler(environment.initState)
    sampler.setTransitionFunction(environment)
    sampler.setPolicy(policy)
    sampler.setRewardFunction(reward)

    data = dataManager.createDataObject([10, 100])

    statesTarget = np.array(range(1, 41))

    pr = cProfile.Profile()
    pr.enable()
    sampler.createSamples(data, [slice(0, 10)])
    states = data.getDataEntry('states', 1)
    actions = data.getDataEntry('actions', 2)
    rewards = data.getDataEntry('rewards', 3)


    pr.disable()
    # after your program ends
    pr.print_stats(sort="time")
    pr.create_stats()
    pr.dump_stats('out.profile2')
