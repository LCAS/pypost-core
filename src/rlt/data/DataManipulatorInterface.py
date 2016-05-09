from enum import Enum

CallType = Enum('CallType', 'SINGLE_SAMPLE ALL_AT_ONCE PER_EPISODE')


class DataManipulatorInterface():
    '''
    The interface for the DataManipulator
    '''

    def __init__(self):
        super().__init__()

    def addDataManipulationFunction(self, function, inputArguments,
                                    outputArguments,
                                    callType=CallType.ALL_AT_ONCE,
                                    takesNumElements=False):
        raise NotImplementedError("Not implemented")

    def addDataFunctionAlias(self, aliasName, functionName, pushToFront=False):
        raise NotImplementedError("Not implemented")

    def isSamplerFunction(self, samplerName):
        raise NotImplementedError("Not implemented")

    def setTakesData(self, name, takesData):
        raise NotImplementedError("Not implemented")

    def setIndices(self, name, numInput, indices):
        raise NotImplementedError("Not implemented")

    def clearDataFunctionAlias(self, alias):
        raise NotImplementedError("Not implemented")

    def callDataFunction(self, samplerName, data, indices):
        raise NotImplementedError("Not implemented")

    def callDataFunctionOutput(self, samplerName, data, indices):
        raise NotImplementedError("Not implemented")
