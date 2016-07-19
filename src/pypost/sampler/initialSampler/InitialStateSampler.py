import abc
from pypost.data.DataManipulator import DataManipulator

class InitialStateSampler(DataManipulator):

    def __init__(self, dataSampler):
        super().__init__(dataSampler.dataManager)
        self.addDataManipulationFunction(self.sampleInitState, [], ['states'], True, True)

    @abc.abstractmethod
    def sampleInitState(self, numElements, *args):
        return