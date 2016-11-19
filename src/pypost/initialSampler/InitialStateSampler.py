import abc
from pypost.mappings import Mapping

class InitialStateSampler(Mapping):

    def __init__(self, dataManager):
        super().__init__(dataManager, inputVariables=None, outputVariables=['states'])
        #self.addDataManipulationFunction(self.sampleInitState, [], ['states'], True, True)

    @Mapping.MappingMethod()
    @abc.abstractmethod
    def sampleInitState(self, numElements, *args):
        return