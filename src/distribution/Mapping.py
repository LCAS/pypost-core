'''
Created on 09.01.2016

@author: Moritz
'''
from interfaces import MappingInterface
from data import DataManager
from data import DataManipulator


class Mapping(MappingInterface, DataManipulator):
    '''
    classdocs
    '''

    def __init__(
            self, dataManager, inputVariables, outputVariable, mappingName=""):
        '''
        Constructor
        @param dataManager: the data manager the mapping is operating on
        @param inputVariables: iterable of input variable names
        @param outputVariable: name of the output variable
        @param mappingName: name of the mapping

        @change: dataManager was removed from function arguments and is now a constructor argument.
        '''
        MappingInterface.__init__()
        DataManipulator.__init__(dataManager, function, inputArguments, outputArguments, depthEntry,
                                 indices, takesNumElements, callType)

        self.dataManager = dataManager
        '''
        the data manager the mapping is operating on
        '''

        self.mappingName = mappingName
        '''
        Name of the mapping
        '''

        self.inputVariables = inputVariables
        '''
        iterable of input variable names
        '''

        self.additionalVariables = {}

        self.outputVariable = {}
        '''
        name of the output variable
        '''

        self.dimInput = {}

        self.dimOutput = {}

        self.mappingFunctions = {}

        self.mappingFunctionsOutputVars = {}

        self.registeredMappingFunction = False

        self.registerDataFunctions = True
