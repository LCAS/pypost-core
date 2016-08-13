import numbers


from pypost.data.DataManipulator import CallType
from pypost.data.DataManipulator import DataManipulator
from pypost.data.DataManipulator import DataManipulationStructure
from pypost.data.DataManipulator import _DataDecorator
from pypost.data.Data import Data

from pypost.data.DataManipulator import ManipulatorMetaClass
# class _DataMappingDecorator(_DataDecorator):
#
#     def __init__(self, function, inputArguments, outputArguments, **kwargs):
#
#         self = _DataDecorator.__init__(function, inputArguments, outputArguments, **kwargs)
#
#
#     def getWrapperFunction(self):
#         dataStruct = self.dataStruct
#
#         def data_function( object, data, indices=Ellipsis, registerOutput=True):
#
#             if not dataStruct.isInitialized:
#                 dataStruct.isInitialized = True
#
#                 # If we are currently using a suffix stack for the names, impose the suffix to all data entries if we can
#                 # find the name with the suffix. Suffix imposement can be avoided by manually putting "NoSuffix" as a suffix.
#                 # The "NoSuffix" string will be deleted.
#
#                 if dataStruct.outputArguments is None:
#                     dataStruct.outputArguments = object.getOutputVariables()
#                 else:
#                     for i in range(0, len(dataStruct.outputArguments)):
#                         if (dataStruct.outputArguments[i] == '_outputDataMapping_'):
#                             dataStruct.outputArguments[i] = object.getOutputVariables()[0]
#
#                 if (dataStruct.inputArguments is None):
#                     dataStruct.inputArguments = object.getInputVariables()
#                 else:
#                     newInputArguments = []
#                     for i in range(0, len(dataStruct.inputArguments)):
#                         if (dataStruct.inputArguments[i] == '_inputDataMapping_'):
#                             newInputArguments = newInputArguments + object.getInputVariables()
#                         else:
#                             newInputArguments.append(dataStruct.inputArguments[i])
#
#                 self.preprocessArguments(object, dataStruct)
#
#             output = _DataDecorator._callDataFunctionInternal(dataStruct, data, indices, registerOutput)
#             return output
#         return data_function



class MappingMetaClass(ManipulatorMetaClass):
    def __init__(cls, name, bases, dct):

        super(MappingMetaClass, cls).__init__(name, bases, dct)
        cloneDict = cls.__dict__.copy()
        numMappingFunctions = 0
        for (key, function) in cloneDict.items():

            if hasattr(function, 'initializeAsMappingFunction') and function.initializeAsMappingFunction:

                if (numMappingFunctions == 0):
                    name = function.__name__
                    setattr(cls, 'callFunctionName', name)
                    function.initializeAsMappingFunction = False
                    setattr(cls, name, function)
                    cls.dataFunction = cls.__call__
                    numMappingFunctions += 1
                else:
                    raise ValueError('A mapping can only have one mapping function')


class Mapping(DataManipulator, metaclass=MappingMetaClass):
    '''
    The Mapping class is a DataManipulator that is able to combine a
    number of data manipulation functions.

    Every Mapping contains a set of data manipulation function as well as
    sets for the input and output variables. The input and output can be
    defined in the constructor or at a later point via setInputVariables()
    and setOutputVariables(). New mapping functions have to be
    added with the addMappingFunction()
    '''
    callFunctionName = ''

    @staticmethod
    def DataMappingFunction(inputArguments = 'self.inputVariables', outputArguments = 'self.outputVariables', callType=CallType.ALL_AT_ONCE, takesNumElements=False,
                            takesData=False):

        def wrapper(function):
            decorator = _DataDecorator(function, inputArguments, outputArguments, callType, takesNumElements,
                                       takesData)
            function.dataFunctionDecorator = decorator
            function.initializeAsMappingFunction = True
            return function

        return wrapper


    def __init__(self, dataManager, inputVariables=None, outputVariables=None,
                 name=""):
        '''
        Constructor

        :param dataManager: the data manager the mapping is operating on
        :param inputVariables: iterable of input variable names
        :param outputVariables: name of the output variable
        :param name: name of the mapping

        :change: dataManager was removed from function arguments and is now a constructor argument.
        :change: registeredMappingFunctions was never used and got deleted
        :change: registerDataFunctions is eqivalent to inputVariables = empty
        #FIXME check registerDataFunctions invariant again
        '''
        DataManipulator.__init__(self, dataManager)

        self.name = name
        '''
        Name of the mapping function
        '''
        self.inputVariables = []
        '''
        Input variables for mapping functions
        '''
        if inputVariables is not None:
            self.setInputVariables(inputVariables)

        self.outputVariables = None
        '''
        Output variables for mapping functions
        '''
        if outputVariables is not None:
            self.setOutputVariables(outputVariables)

        self.callFunctionData = None
        self.callFunctionPlain = None

    def getNumElementsAndInput(self, input):
        if (len(self.inputVariables) > 0):
            numElements = input.shape[0]
        else:
            numElements = input
            input = None
        return (numElements, input)

    def setMappingCallFunction(self, callFunctionName):
        self.callFunctionName = callFunctionName

    @DataManipulator.DataFunction
    def __call__(self, *args, fromData = True):

        if (fromData):
            if (len(args) == 0 or not isinstance(args[0], Data)):
                raise ValueError("Call function requires data as input. Call it with 'fromData = False' to access original function")
            if (self.callFunctionData is None):
                if (not self.callFunctionName):
                    raise ValueError("Call Function of Mapping {0} is not set!".format(self.name))
                self.callFunctionData = getattr(self, self.callFunctionName + '_fromData')
            output =  self.callFunctionData(*args)
        else:
            if (self.callFunctionPlain is None):
                if (not self.callFunctionName):
                    raise ValueError("Call Function of Mapping {0} is not set!".format(self.name))
                self.callFunctionPlain = getattr(self, self.callFunctionName)
            output = self.callFunctionPlain(*args)
        return output

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
                raise DeprecationWarning('inputVariables has to be an array')

            self.inputVariables = inputVariables

        self.dimInput = self.dataManager.getNumDimensions(self.inputVariables)

    def getInputVariables(self):
        return list(self.inputVariables)

    def getOutputVariables(self):
        return list(self.outputVariables)

    def setOutputVariables(self, outputVariables):

        if (not isinstance(outputVariables, list)):
            outputVariables = [outputVariables]

        self.outputVariables = outputVariables
        self.dimOutput = self.dataManager.getNumDimensions(
            self.outputVariables)

        # TODO there was a call to setOutputArguments but I didn't find a
        # single definition of this function anywhere in the code ^moritz

    def setOutputDimension(self, dimension):
        self.dimOutput = dimension
        self.outputVariables = []

