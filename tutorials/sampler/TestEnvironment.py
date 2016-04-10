from data.DataManipulator import DataManipulator
import numpy as np

'''
This is a TestEnvironment to be used by other tutorials.
'''

class TestEnvironment(DataManipulator):
    def __init__(self, dataManager, numContext=2, numAction=5):
        DataManipulator.__init__(self, dataManager)

        self.numContext = numContext
        self.numAction = numAction
        self.dataManager = dataManager

        self.dataManager.addDataEntry(
            'contexts',
            self.numContext,
            -np.ones((self.numContext)),
            np.ones((self.numContext)))

        dataManager.addDataEntry(
            'rewards',
            1,
            -np.ones((1)),
            np.ones((1)))

        dataManager.addDataEntry(
            'parameters',
            self.numAction,
            -np.ones((self.numAction)),
            np.ones((self.numAction)))


        self.addDataManipulationFunction(self.sampleContext, [], ['contexts'])
        self.addDataManipulationFunction(
            self.sampleAction, ['contexts'], ['parameters'])
        self.addDataManipulationFunction(
            self.sampleReward, ['contexts', 'parameters'], ['rewards'])
        self.addDataFunctionAlias('sampleParameter', 'sampleAction')
        self.addDataFunctionAlias('sampleReturn', 'sampleReward')

    def sampleContext(self, numElements):
        return np.random.randn(numElements, self.numContext)

    def sampleAction(self, context):
        return np.random.randn(context.shape[0], self.numAction)

    def sampleReward(self, context, action):
        return np.random.randn(context.shape[0], 1)
