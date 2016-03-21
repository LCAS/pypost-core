import numbers

from functions.MappingInterface import MappingInterface
from data.DataManipulatorInterface import CallType
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

    def __init__(self, dataManager, inputVariables=None,
                 outputVariables=None, name=""):
        '''
        Constructor

        :param dataManager: the data manager the mapping is operating on
        :param inputVariables: iterable of input variable names
        :param outputVariable: name of the output variable
        :param name: name of the mapping

        :change: dataManager was removed from function arguments and is now a constructor argument.
        :change: registeredMappingFunctions was never used and got deleted
        :change: registerDataFunctions is eqivalent to inputVariables = empty
        #FIXME check registerDataFunctions invariant again
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

        self.inputVariables = []
        '''
        Input variables for mapping functions
        '''
        if inputVariables is not None:
            self.setInputVariables(inputVariables)

        self.additionalInputVariables = []

        self.outputVariables = []
        '''
        Output variables for mapping functions
        '''
        if outputVariables is not None:
            self.setOutputVariables(outputVariables)

        # self.dimInput = {}

        # self.dimOutput = {}
        # TODO: check the following line
        print(self.dimOutput)
        self.dimOutput = self.dataManager.getNumDimensions(self.outputVariable)

        self.mappingFunctions = []

    def getAdditionalInputVariables(self):
        return list(self.additionalInputVariables)

    def setAdditionalInputVariables(self, variables):
        self.additionalInputVariables = variables

    def addMappingFunction(self, function, outputVariables=None,
                           functionName=None):
        '''
        Add a mapping function

        :param function: the function to add to the mapping
        :param outputVariables: new output variables. defaults to the Mapping
                                output variables if not set
        :param functionName: name to register the function to

        By adding a new mapping function the Mapping will register
        a new DataManipulationFunction in the DataManager, with
        the currently defined inputVariables and the current set of
        outputVariables also including the new outputVariables added
        in this function call. (see also Data.DataManipulator)
        '''
        if outputVariables is None:
            outputVariables = self.outputVariables

        self.mappingFunctions.append(function)

        inputVars = []
        inputVars.extend(self.inputVariables)
        inputVars.extend(self.additionalInputVariables)

        self.addDataManipulationFunction(
            self.mappingFunctions[-1],
            inputVars,
            outputVariables,
            None,
            True,
            functionName
        )

    # change registerMappingFunction was never used and referenced
    # self.outputVariables[1] which doesn't even exist

    def setInputVariables(self, inputVariables, numDim=None, append=False):
        '''Sets the input variables given to each mapping function registered
        by this Mapping

        :param inputVariables: iterable of input variable names
        :param numDim: optional parameter indicating the input dimension. currently not supported!
        :param append: set to true to keep the current input variables
        '''
        if numDim is not None:
            raise NotImplementedError("Number arguments are not supported")

        if len(inputVariables) != 0 and isinstance(
                inputVariables[0], numbers.Number):
            '''
            :trap: catches 1:1 code translations from Matlab where the first
            inputVariables argument could be a number. this functionality can
            now be reached by using the numDim argument

            > Currently there are no number arguments supported.
            > Look into the Matlab code for more detail.
            '''
            raise DeprecationWarning("Function interface changed, the numDim" +
                " parameter now hold the number of dimensions")

        if append:
            self.inputVariables.extend(inputVariables)
        else:
            if isinstance(inputVariables, str):
                raise ValueError('inputVariables has to be an array')

            self.inputVariables = inputVariables

        print(self.inputVariables)
        self.dimInput = self.dataManager.getNumDimensions(self.inputVariables)
        print(self.dimInput)

    def getInputVariables(self):
        return list(self.inputVariables)

    def getOutputVariables(self):
        return list(self.outputVariables)

    def setOutputVariables(self, outputVariables):
        if len(outputVariables) > 1:
            raise RuntimeError("Only single output variable supported")

        self.outputVariables = outputVariables
        self.dimOutput = self.dataManager.getNumDimensions(self.outputVariables)
        print(outputVariables, self.dimOutput)

    # def cloneDataManipulationFunctions(self, cloneDataManipulator):
        #raise "Not implemented"
        # FIXME design of this class is not finally finished
        #    self.cloneDataManipulationFunctions@Data.DataManipulator(cloneDataManipulator);
        #    self.inputVariables = cloneDataManipulator.inputVariables;
        #    self.outputVariable = cloneDataManipulator.outputVariable;
        #    self.dimInput = self.dataManager.getNumDimensions(self.inputVariables);
        #    self.dimOutput = self.dataManager.getNumDimensions(self.outputVariable);
        # end
