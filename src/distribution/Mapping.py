'''
Created on 09.01.2016

@author: Moritz
'''
import numbers

from interfaces.MappingInterface import MappingInterface
from interfaces.DataManipulatorInterface import CallType
from data.DataManipulator import DataManipulator


class Mapping(DataManipulator, MappingInterface):
    '''
    The Mapping class is a DataManipulator that is able to combine a
    number of data manipulation functions.

    Every Mapping contains a set of data manipulation function as well as
    sets for the input and output variables. The input and output can be
    defined in the constructor or at a later point via setInputVariables()
    and setOutputVariables(). New mapping functions have to be
    added with the addMappingFunction()
    '''

    def __init__(
            self, dataManager, inputVariables=None, outputVariables=None, name=""):
        '''
        Constructor
        @param dataManager: the data manager the mapping is operating on
        @param inputVariables: iterable of input variable names
        @param outputVariable: name of the output variable
        @param name: name of the mapping

        @change: dataManager was removed from function arguments and is now a constructor argument.
        @change: registeredMappingFunctions was never used and got deleted
        @change registerDataFunctions is eqivalent to inputVariables = empty
        #FIXME check registerDataFunctions invariant again, they are doing strange things ...
        '''
        DataManipulator.__init__(self, dataManager)
        MappingInterface.__init__(self)

        self.dataManager = dataManager
        '''
        The data manager the mapping is operating on
        '''

        self.name = name
        '''
        Name of the mapping function
        TODO change to property
        '''

        self.inputVariables = {}
        '''
        Input variables for mapping functions
        '''
        if inputVariables is not None:
            self.setInputVariables(inputVariables)

        self.additionalInputVariables = {}

        self.outputVariables = {}
        '''
        Output variables for mapping functions
        '''
        if outputVariables is not None:
            self.setOutputVariables(outputVariables)

        # self.dimInput = {}

        # self.dimOutput = {}

        self.mappingFunctions = []

    def addAdditionalInputVariables(self, variables):
        self.additionalInputVariables = variables

    def addMappingFunction(self, function, outputVariables=None):
        '''
        @param function: the function to add to the mapping
        @param outputVariables new output variables. defaults to the Mapping output variables if not set

        By adding a new mapping function the Mapping will register
        a new DataManipulationFunction in the DataManager, with
        the currently defined inputVariables and the current set of
        outputVariables also including the new outputVariables added
        in this function call. (see also Data.DataManipulator)
        #FIXME see also DataManipulator -> DataManipulator has no addMappingFunction
        '''
        if outputVariables is None:
            outputVariables = self.outputVariables

        self.mappingFunctions.append(function)

        self.addDataManipulationFunction(
            self.mappingFunctions[-1],
            [
                list(self.inputVariables),
                list(self.additionalInputVariables)
            ],
            outputVariables,
            CallType.ALL_AT_ONCE,
            True
        )

    # change registerMappingFunction was never used and referenced
    # obj.outputvariables[1] which doesn't even exist

    def setInputVariables(self, inputVariables, numDim=0):
        '''
        Sets the input variables given to each mapping function registered by this Mapping
        @param inputVariables: iterable of input variable names
        @param numDim: optional parameter. currently not supported!
        '''

        if len(inputVariables) != 0 and isinstance(
                inputVariables[0], numbers.Number):
            # Currently there are no number arguments supported.
            # Look into the Matlab code for more detail. It can be
            # simply replaced by a mapping function with zero inputs
            # outputting the result for this mapping
            #
            # It seems like if the first inputvar was a number the self.dimInput was set to this
            # search for a cleaner way to model this (e.g. pass as explicit
            # argument and set a flag)
            raise "Number arguments are not supported"

        self.inputVariables = inputVariables

        self.dimInput = self.dataManager.getNumDimensions(self.inputVariables)

    def getInputVariables(self):
        return self.inputVariables

    def getOutputVariable(self):
        return self.outputVariable

    def setOutputVariables(self, outputVariables):
        self.outputVariables = outputVariables

    def cloneDataManipulationFunctions(self, cloneDataManipulator):
        raise "Not implemented"
        # FIXME design of this class is not finally finished
        #    obj.cloneDataManipulationFunctions@Data.DataManipulator(cloneDataManipulator);
        #    obj.inputVariables = cloneDataManipulator.inputVariables;
        #    obj.outputVariable = cloneDataManipulator.outputVariable;
        #    obj.dimInput = obj.dataManager.getNumDimensions(obj.inputVariables);
        #    obj.dimOutput = obj.dataManager.getNumDimensions(obj.outputVariable);
        # end
