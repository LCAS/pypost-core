import numbers


from pypost.data.DataManipulator import CallType
from pypost.data.DataManipulator import DataManipulator
from pypost.data.DataManipulator import DataManipulationFunction
from pypost.data.Data import Data

from pypost.data.DataManipulator import ManipulatorMetaClass

class MappingMetaClass(ManipulatorMetaClass):
    def __init__(cls, name, bases, dct):

        super(MappingMetaClass, cls).__init__(name, bases, dct)

        cloneDict = cls.__dict__.copy()
        for (key, function) in cloneDict.items():

            if (hasattr(function, '__name__')):
                name = function.__name__

                if (hasattr(function, 'isMappingFunction') and  function.isMappingFunction):
                    function.isMappingFunction = False

                    setattr(cls, 'callFunctionName', name)

        if (cls.callFunctionName):
            callFunction = getattr(cls, cls.callFunctionName)
            setattr(cls, '__call__', callFunction)


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

    @classmethod
    def MappingMethod(cls, inputArguments ='self.inputVariables', outputArguments ='self.outputVariables', callType=CallType.ALL_AT_ONCE, takesNumElements=False,
                      takesData=False, lazyEvaluation = False):

        def wrapper(function):
            function.dataFunctionDecorator = DataManipulationFunction(function.__name__, inputArguments, outputArguments,
                                                             callType, takesNumElements, takesData, lazyEvaluation)
            function.isMappingFunction = True
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

        if (self.callFunctionName):
            self.dataFunctionDecorator = self.dataManipulationMethodsInstance[self.callFunctionName]

    def getNumElementsAndInput(self, input):
        if (len(self.inputVariables) > 0):
            numElements = input.shape[0]
        else:
            numElements = input
            input = None
        return (numElements, input)

    def setMappingCallFunction(self, callFunctionName):
        self.callFunctionName = callFunctionName

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

    def isTakesNumElements(self):
        return self.dataFunctionDecorator.takesNumElements

    def isTakesData(self):
        return self.dataFunctionDecorator.takesData

    def getCallType(self):
        return self.dataFunctionDecorator.callType

    def setLazyEvaluation(self, lazyEval):
        self.dataFunctionDecorator.lazyEvaluation = lazyEval

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

    def getDimOutput(self):
        return self.dimOutput

    def getDimInput(self):
        return self.dimInput

