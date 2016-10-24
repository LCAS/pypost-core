import numpy as np
from pypost.envs.TransitionFunction import TransitionFunction

# basically the same implementation as in matlab
class MountainCar(TransitionFunction):

    def __init__(self, episodeManager):
        super().__init__(episodeManager, 2, 1)
        self.numContext = 2
        self.initialState = [-0.5, 0]
        self.goalPosition = 0.5

        self.limitPosition = np.asarray([-1.2, 0.6])
        self.limitVelocity = np.asarray([-0.07, 0.07])

        # f = m * a? => u = f, accelFactor = 1/m? (=> a = u * accelFactor?)
        self.accelFactor = 0.001

        self.gravityFactor = -0.0025

        self.hillPeakFreq = 3.0

        self.transitionNoise = 0.2

        self.episodeManager = episodeManager
        self.stepManager = self.episodeManager.subDataManager

        self.episodeManager.addDataEntry('contexts', self.numContext,
                                         - np.ones(self.numContext), np.ones(self.numContext))
        self.stepManager.setRange('actions', np.asarray([-1]), np.asarray([1]))
        self.stepManager.setRange('states', np.asarray([self.limitPosition[0], self.limitVelocity[0]]),
                                  np.asarray([self.limitPosition[1], self.limitPosition[1]]))

        #self.stepManager.setRange('nextStates', np.asarray([self.limitPosition[0], self.limitVelocity[0]]),
        #                          np.asarray([self.limitPosition[1], self.limitPosition[1]]))

        self.stepManager.addDataEntry('rewards', 1, -1, 1)

        #self.addDataManipulationFunction(self.sampleContext,  [], ['contexts'])
        #self.addDataManipulationFunction(self.sampleAction, ['states'], ['actions'])
        #self.addDataManipulationFunction(self.sampleReward, ['nextStates'], ['rewards'])
        #self.addDataManipulationFunction(self.sampleInitState, ['contexts'], ['states'])

        #self.initObject()

    @TransitionFunction.DataMethod(inputArguments=[], outputArguments=['contexts'], takesNumElements=True)
    def sampleContext(self, numElements):
        return np.tile(self.initialState, (numElements, 1))

    @TransitionFunction.DataMethod(inputArguments=['contexts'], outputArguments=['states'])
    def sampleInitState(self, context):
        return context[:, 0:2]

    @TransitionFunction.DataMethod(inputArguments=['states', 'actions'], outputArguments=['nextStates'])
    def transitionFunction(self, state, action):
        noise = 2 * self.accelFactor * self.transitionNoise * (np.random.normal(size=action.shape) - 0.5)

        # Current Velocity + Noise + u * a + cos( ? * pos ) * g
        nextVelocity = state[:, 1:2] + noise + \
                       action * self.accelFactor + np.cos(self.hillPeakFreq * state[:, 0:1]) * self.gravityFactor

        nextPosition = state[:, 0:1] + nextVelocity
        # Upper limit
        nextVelocity = np.maximum(np.minimum(self.limitVelocity[1], nextVelocity), self.limitVelocity[0])
        nextPosition = np.minimum(self.limitPosition[1], nextPosition)
        # Lower limit (according to matlab reference no lower limit for position, why?)

        nextState = np.concatenate((nextPosition, nextVelocity), 1)
        return nextState

    @TransitionFunction.DataMethod(inputArguments=['states'], outputArguments=['actions'])
    def sampleAction(self, state):
        return np.random.rand(np.shape(state)[0], 1) * 2 - 1

    @TransitionFunction.DataMethod(inputArguments=['nextStates'], outputArguments=['rewards'])
    def sampleReward(self, nextState):
        return np.reshape((nextState[:, 1] > self.goalPosition) - 1, (-1, 1))