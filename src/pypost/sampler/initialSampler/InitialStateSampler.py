import abc
from pypost.data.DataManipulator import DataManipulator

class InitialStateSampler(DataManipulator):

    def __init__(self, dataManager):
        super().__init__(dataManager)
        #self.addDataManipulationFunction(self.sampleInitState, [], ['states'], True, True)

    @DataManipulator.DataMethod(inputArguments=[], outputArguments=['states'])
    @abc.abstractmethod
    def sampleInitState(self, numElements, *args):
        return