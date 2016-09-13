import numpy as np

from pypost.sampler import EpisodeSampler
from pypost.data import DataManipulator
from pypost.mappings import Mapping
'''
In this tutorial, we will learn how to create samples
'''


class TestReturn(DataManipulator):
    def __init__(self, dataManager):
        DataManipulator.__init__(self, dataManager)

    @DataManipulator.DataMethod([], ['contexts'])
    def sampleContexts(self, numElements):
        return np.ones((numElements, self.dataManager.getNumDimensions('contexts')))

    @DataManipulator.DataMethod(['contexts', 'parameters'], ['returns'])
    def sampleReturns(self, contexts, parameters):
        temp = np.sum(contexts + parameters, 1)
        temp.resize(contexts.shape[0], 1)
        return temp

class TestPolicy(Mapping):
    def __init__(self, dataManager):
        Mapping.__init__(self, dataManager, inputVariables=['contexts'], outputVariables='parameters')

    @Mapping.MappingMethod()
    def sampleParameters(self, contexts):
        return np.ones((contexts.shape[0], self.dataManager.getNumDimensions('contexts'))) + contexts


sampler = EpisodeSampler()
dataManager = sampler.dataManager

dataManager.addDataEntry('contexts', 2)
dataManager.addDataEntry('parameters', 2)
dataManager.addDataEntry('returns', 1)

environment = TestReturn(dataManager)
policy = TestPolicy(dataManager)

sampler.setContextSampler(environment.sampleContexts)
sampler.setParameterPolicy(policy)
sampler.setReturnFunction(environment.sampleReturns)

newData = dataManager.getDataObject(10)

newData[...] >> sampler

print('Contexts:', newData[...].contexts)
print('Parameters:', newData[...].parameters)
print('Returns:', newData[...].returns)

