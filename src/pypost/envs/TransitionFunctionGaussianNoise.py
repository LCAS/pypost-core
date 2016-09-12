import abc

from pypost.envs.TransitionFunction import TransitionFunction


class TransitionFunctionGaussianNoise(TransitionFunction):

    def __init__(self, dataManager, dimState, dimAction):
        super().__init__(dataManager, dimState, dimAction)

    @abc.abstractmethod
    @TransitionFunction.DataMethod(inputArguments=['states', 'actions'], outputArguments=['nextStates'])
    def getExpectedNextState(self, *args):
        return

    @abc.abstractmethod
    @TransitionFunction.DataMethod(inputArguments=['states', 'actions'], outputArguments=['systemNoise'])
    def getSystemNoiseCovariance(self, *args):
        return



