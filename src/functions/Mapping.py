import numpy as np
from data.DataManipulator import DataManipulator


class Mapping(DataManipulator):
    '''
    The Mapping class is a DataManipulator that is able to combine a
    number of data manipulation functions.

    Every Mapping contains a set of data manipulation function as well as
    sets for the input and output variables. The input and output can be
    defined in the constructor or at a later point via `setInputVariables()`
    and `setOutputVariables()`. New mapping functinos have to be
    added with the `addMappingFunction()`.
    '''

    def __init__(self, dataManager, outputVariable, inputVariables,
                mappingName='function'):
        '''
        :param dataManager: DataManager this mapping operates
        :param outputVariable: name of the data entry to which this mapping
                               will output
        :param inputVariables: name of the data entry from which this mapping
                               will get input
        :param mappingName: name of this mapping (Default: 'function')
        '''
        DataManipulator.__init__(self, dataManager)

        self.inputVariables = [] # collection of input Variables
        self.additionalInputVariables = []
        self.outputVariable = [] # collection of output Variables
        self.mappingFunctions = [] # collection of mapping functions
        self.mappingFunctionsOutputVariables = [] # collection of the output
                                                  # variables of the functions,
                                                  # not necessarily equal to
                                                  # outputVariable
        self.registeredMappingFunctions = False # flag indicating if any
                                                # mapping functions have been
                                                # included in this Mapping
        self.registerDataFunctions = True

        DataManipulator(dataManager)

        self.dataManager = dataManager
        self.setOutputVariables(outputVariable)
        self.setInputVariables(inputVariables)
        self.mappingName = mappingName

    def setAdditionalInputVariables(self, varargin):
        # TODO: check this
        self.additionalInputVariables = varargin

    def addMappingFunction(self, mappingFunctionName, outputVariables):
        '''
        :param mappingFunctionName: Name of the new mapping function
        :param outputVariables: optional new output variables

        by adding a new mapping function the Mapping will register
        a new DataManipulationFunction in the Data.DataManager, with
        the currently defined inputVariables and the current set of
        outputVariables also including the new outputVariables added
        in this function call. (see also data.DataManipulator)
        '''

        self.mappingFunctions.append(mappingFunctionName)
        self.mappingFunctionsOutputVariables.append([])

        for i in range(0, len(outputVariables)):
            self.mappingFunctionsOutputVariables[-1][i] =\
                np.hstack([self.outputVariable, outputVariables[i]])

        # TODO: check
        self.addDataManipulationFunction(
            self.mappingFunctions[-1],
            np.hstack([self.inputVariables, self.additionalInputVariables]), self.mappingFunctionsOutputVariables[-1], True, True)

    # FIXME what does this matlab-syntax mean?
    #def getDepthEntryForDataManipulationFunction(obj, ~, ~):
    #    return = self.outputVariable

    def registerMappingFunction(self):
        self.registeredMappingFunctions = True

        for i in range(0, len(self.mappingFunctions)):
            self.addDataManipulationFunction(
                self.mappingFunctions[i],
                np.hstack([self.inputVariables,
                           self.additionalInputVariables[:]]),
                np.hstack([self.outputVariables[0],
                           self.mappingFunctionsOutputVariables[i]]),
                True, True)

    def setMappingName(self, name):
        self.mappingName = name

    def setInputVariables(self, varargin):
        self.inputVariables = varargin;

        if self.inputVariables is not None:
            if isinstance(self.inputVariables[0], np.ndarray):
                self.dimInput = self.dataManager.getNumDimensions(
                    self.inputVariables);

                for i in range(0, len(self.mappingFunctions)):
                    self.setInputArguments(
                        self.mappingFunctions[i],
                        self.inputVariables,
                        self.additionalInputVariables[0])
            else:
                self.dimInput = self.inputVariables[1]
                self.registerDataFunctions = False
        else:
            self.dimInput = 0;

    def getInputVariable(self, index):
        return self.inputVariables[index]


    def setOutputVariables(self, outputArgument):
        if isinstance(outputArgument, np.ndarray):
            self.dimOutput = outputArgument
            self.outputVariable = []

            if self.registerDataFunctions:
                for i in range(0, len(self.mappingFunctions)):
                    self.setOutputArguments(
                        self.mappingFunctions[i],
                        [self.mappingFunctionsOutputVariables[i]])
        else:
            self.outputVariable = outputArgument

            self.dimOutput =\
                self.dataManager.getNumDimensions(self.outputVariable)

            for i in range(0, len(self.mappingFunctions)):
                self.setOutputArguments(
                    self.mappingFunctions[i],
                    np.hstack([outputArgument,
                               self.mappingFunctionsOutputVariables[i]]))

    def getOutputVariable(self):
        return self.outputVariable

    def cloneDataManipulationFunctions(self, cloneDataManipulator):
        self.cloneDataManipulationFunctions(cloneDataManipulator)
        self.inputVariables = cloneDataManipulator.inputVariables;
        self.outputVariable = cloneDataManipulator.outputVariable;
        self.dimInput = self.dataManager.getNumDimensions(self.inputVariables)
        self.dimOutput = self.dataManager.getNumDimensions(self.outputVariable)
