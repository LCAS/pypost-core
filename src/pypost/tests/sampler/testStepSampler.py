import unittest
from pypost.tests import DataUtil
from pypost.sampler.StepSampler import StepSampler
from pypost.sampler.EpisodeWithStepsSampler import EpisodeWithStepsSampler
from pypost.sampler.Sampler import Sampler
from pypost.functions.Mapping import Mapping
from pypost.data.DataManipulator import DataManipulator
from pypost.data.DataManipulator import DataManipulationFunction
from pypost.common.SettingsManager import *


import numpy as np
import cProfile


@DataManipulationFunction(inputArguments=[], outputArguments=['states'])
def initState(numElements):
    return np.ones((numElements, 1))


class TestEnvironment(Mapping):

    def __init__(self, dataManager, inputVariables = ['states', 'actions'], outputVariables = ['nextStates']):
        Mapping.__init__(self, dataManager, inputVariables, outputVariables)

    @Mapping.DataMappingFunction()
    def transitionFunction(self, states, actions):
        return states + 1


class TestPolicy(Mapping):
    mappingFunctionName = 'getAction'

    def __init__(self, dataManager):
        Mapping.__init__(self, dataManager, ['states'], ['actions'])

    @Mapping.DataMappingFunction()
    def getAction(self, states):
        return states * 2

class TestReward(Mapping):
    mappingFunctionName = 'getReward'

    def __init__(self, dataManager):
        Mapping.__init__(self, dataManager, ['states', 'actions'], ['rewards'])

    @Mapping.DataMappingFunction()
    def getReward(self, states, actions):
        return states * 2

class testStepSampler(unittest.TestCase):


    def setUp(self):
        self.dataManager = DataUtil.createTestManagerSteps()
        self.sampler = StepSampler(self.dataManager, 'steps')

        #Todo: get function for data manager
    def tearDown(self):
        pass

    def test_init(self):
        self.assertIsInstance(self.sampler, StepSampler)
        self.assertIsNotNone(self.sampler.getSamplerPool('InitSamples'))
        self.assertIsNotNone(self.sampler.getSamplerPool('Policy'))
        self.assertIsNotNone(self.sampler.getSamplerPool('TransitionSampler'))
        self.assertIsNotNone(self.sampler.getSamplerPool('RewardSampler'))
        self.assertTrue(self.sampler.dataManager.isDataEntry('timeSteps'))

    def testSampling(self):

        settings = getDefaultSettings()
        settings.numTimeSteps = 40
        environment = TestEnvironment(self.dataManager)
        policy = TestPolicy(self.dataManager)
        reward = TestReward(self.dataManager)

        self.sampler.setInitStateSampler(initState)
        self.sampler.setTransitionFunction(environment)
        self.sampler.setPolicy(policy)
        self.sampler.setRewardFunction(reward)

        data = self.dataManager.getDataObject([10, 100])
        self.sampler.createSamples(data, [slice(0,10)])

        states = data.getDataEntry('states', 1)
        actions = data.getDataEntry('actions', 2)
        rewards = data.getDataEntry('rewards', 3)

        statesTarget = np.array(range(1,41))
        self.assertTrue( (abs(states.transpose() - statesTarget ) < 0.00001).all())
        self.assertTrue((abs(states * 2 - actions) < 0.00001).all())
        self.assertTrue((abs(states * 2- rewards) < 0.00001).all())




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']

    unittest.main()

