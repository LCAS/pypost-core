from pypost.sampler import EpisodeWithStepsSampler
from pypost.data import DataManager
from pypost.data import DataType
from pypost.data import DataManipulator


import numpy as np

import gym
from gym import spaces
from gym.utils import seeding


class GymSampler(EpisodeWithStepsSampler):

    def __init__(self, gymEnvironment, useRender = False):


        dataManager = DataManager(['episodes', 'steps'])

        dataManager.subDataManager.addDataEntry('rewards', 1)
        dataManager.subDataManager.addDataEntry('isTerminalState', 1, dataType=DataType.discrete)

        if isinstance(gymEnvironment.observation_space, spaces.Box):
            low = gymEnvironment.observation_space.low
            high = gymEnvironment.observation_space.high
            dataManager.addDataEntry('states', low.shape, low, high, level=1)
        elif isinstance(gymEnvironment.observation_space, spaces.Discrete):
            dataManager.addDataEntry('states', 1, np.array([1]), np.array([gymEnvironment.observation_space.n]), dataType=DataType.discrete, level=1)

        if isinstance(gymEnvironment.action_space, spaces.Box):
            low = gymEnvironment.action_space.low
            high = gymEnvironment.action_space.high
            dataManager.addDataEntry('actions', low.shape, low, high, level=1)
        elif isinstance(gymEnvironment.observation_space, spaces.Discrete):
            dataManager.addDataEntry('actions', 1, np.array([1]),
                                                    np.array([gymEnvironment.action_space.n]),dataType=DataType.discrete, level=1)

        # get one step to check the info
        gymEnvironment.reset()
        observation, reward, done, info = gymEnvironment.step(gymEnvironment.action_space.sample())

        self.outputArgumentsStep = ['nextStates', 'rewards', 'isTerminalState']
        for key, value in info.items():
            if (isinstance(value,np.ndarray)):
                dataManager.addDataEntry(key, value.shape, level=1)
                self.outputArgumentsStep.append(key)

        super().__init__(self, dataManager)
        self.gymEnvironment = gymEnvironment

        self._parallelSampling = False



    @DataManipulator.DataMethod(inputArguments=['actions'], outputArguments=['self.outputArgumentsStep'])
    def nextStep(self, action):
        observation, reward, done, info = self.gymEnvironment.step(action)

        returnList = [observation, reward, info]
        for key, value in info.items():
            if (isinstance(value, np.ndarray)):
                returnList.append(value)

        return returnList

    @DataManipulator.DataMethod(inputArguments=[''], outputArguments=['states'])
    def reset(self):
        return self.gymEnvironment.reset()

    @DataManipulator.DataMethod(inputArguments=[''], outputArguments=[''])
    def render(self):
        self.gymEnvironment.render()