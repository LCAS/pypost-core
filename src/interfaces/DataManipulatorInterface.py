'''
Created on 22.11.2015

@author: Moritz
'''

from enum import Enum

CallType = Enum('CallType', 'SINGLE_SAMPLE ALL_AT_ONCE PER_EPISODE')


class DataManipulatorInterface(object):
    '''
    FIXME
    '''

    def __init__(self):
        '''
        Constructor
        '''
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

    def clearDataFunctionAlias(self, alias):
        raise NotImplementedError("Not implemented")

    def callDataFunction(self, samplerName, data, indices):
        raise NotImplementedError("Not implemented")

    def callDataFunctionOutput(self, samplerName, data, indices):
        raise NotImplementedError("Not implemented")