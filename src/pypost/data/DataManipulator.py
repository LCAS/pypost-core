from pypost.data.DataManager import DataManager
from pypost.common.SettingsClient import SettingsClient
import numpy as np
from enum import Enum

import copy

CallType = Enum('CallType', 'SINGLE_SAMPLE ALL_AT_ONCE PER_EPISODE')




class DataManipulationStructure():
    '''
    Represents a data manipulation function used in the DataManipulator class.
    '''

    def __init__(self, function, inputArguments, outputArguments, callType = CallType.ALL_AT_ONCE, takesNumElements = False, takesData = False):
        '''
        Constructor
        '''

        self.function = function
        self.inputArguments = inputArguments
        self.outputArguments = outputArguments
        self.takesData = takesData
        self.callType = callType
        self.takesNumElements = takesNumElements
        self.isInitialized = False
        self.depthEntry = None

        if not isinstance(self.inputArguments, list):
            self.inputArguments = [self.inputArguments]

        if not isinstance(self.outputArguments, list):
            self.outputArguments = [self.outputArguments]

    def __str__(self):
        return "%s: %s -> %s" % (self.function.__name__, self.inputArguments,
                                 self.outputArguments)

def DataManipulationFunction(inputArguments, outputArguments, callType = CallType.ALL_AT_ONCE, takesNumElements = False, takesData = False):
    def wrapper(function):
        if (hasattr(function, '__self__')):
            raise ValueError('For class methods, please use the DataManipulator.DataManipulationMethod decorator')

        dataDecorator = _DataDecorator(function, inputArguments, outputArguments, callType, takesNumElements, takesData)
        newFunction = dataDecorator.getWrapperFunction(isMethod=False)
        newFunction.dataFunction = newFunction
        return newFunction
    return wrapper


class _DataDecorator:

    def __init__(self,function, inputArguments, outputArguments, callType = CallType.ALL_AT_ONCE, takesNumElements = False, takesData = False):

        self.dataStruct = DataManipulationStructure(function, inputArguments, outputArguments, callType, takesNumElements, takesData)


    @staticmethod
    def _callDataFunctionInternal(object, dataStruct,  data, indices, registerOutput):

        '''
        Calls the data function using the right call type.
        If registerOutput is set, the resulting data will be written back
        into the object.
        '''
        callData = True

        if dataStruct.callType is CallType.PER_EPISODE:
            indices = data.completeLayerIndex(1, indices)
        elif dataStruct.callType is CallType.SINGLE_SAMPLE:
            for i in range(0, len(indices)):
                if not isinstance(indices[i], int):
                    raise ValueError("SINGLE_SAMPLE functions cannot be called"
                                     " with multiple input values")
            indices = data.completeLayerIndex(
                data.dataManager.getDataEntryDepth(
                    dataStruct.depthEntry), indices)

        if dataStruct.callType is CallType.SINGLE_SAMPLE or \
                        dataStruct.callType is CallType.PER_EPISODE:
            outArgs = None
            numLayers = len(indices)
            if dataStruct.callType is CallType.PER_EPISODE:
                numLayers = 1
            for i in range(0, numLayers):
                if isinstance(indices[i], slice):
                    # This is somewhat hacky, but it works!
                    # Maybe clone data and get shape directly?
                    indexRange = range(0, indices[i].stop)[indices[i]]

                    if len(indexRange) > 1:
                        callData = False
                        for j in indexRange:
                            indicesSingle = indices
                            indicesSingle[i] = slice(j, j + 1)
                            if registerOutput:
                                _DataDecorator._callDataFunctionInternal(object, dataStruct,
                                    data,
                                    registerOutput,
                                    indicesSingle)
                            else:
                                tempOut = _DataDecorator._callDataFunctionInternal(object, dataStruct,
                                    data,
                                    registerOutput,
                                    indicesSingle)
                                if outArgs is None:
                                    outArgs = tempOut
                                else:
                                    for i in range(0, len(outArgs)):
                                        outArgs[i] = np.vstack((outArgs[i],
                                                                tempOut[i]))

        if callData:
            inputArgs = data.getDataEntryList(dataStruct.inputArguments, indices)


            numElements = None
            if dataStruct.takesNumElements and dataStruct.depthEntry:
                outputDepth = data.dataManager.getDataEntryDepth(dataStruct.depthEntry)
                numElements = data.getNumElementsForIndex(outputDepth, indices)
            else:
                numElements = 0

            outArgs = _DataDecorator._callDataFuntionInternalMatrices(object, dataStruct, data, numElements, inputArgs)

            if not isinstance(outArgs, list):  # pragma: no branch
                outArgList = [outArgs]
            else:
                outArgList = outArgs

            if registerOutput:
                if (len(outArgList) < len(dataStruct.outputArguments) or not all(x is not None for x in outArgList[:len(dataStruct.outputArguments)]) ):
                    raise ValueError("Function {0} must return {1} values which are not None".format(dataStruct.function.__name__, len(dataStruct.outputArguments)))
                try:
                    data.setDataEntryList(dataStruct.outputArguments, indices, outArgList)
                except ValueError as error:
                    raise ValueError('Error when registering output arguments of function ' + dataStruct.function.__name__ +
                                     ': ' + error.args[0] + '. Please check your output arguments!')
        return outArgs

    @staticmethod
    def _callDataFuntionInternalMatrices(object, dataStruct, data, numElements, inputArgs):
        '''
        Directly calls the manipulation function and returns the result matrix.
        '''
        args = []
        if dataStruct.takesNumElements:
            args.append(numElements)
        if dataStruct.takesData:
            args.append(data)

        args.extend(inputArgs)
        args = tuple(args)

        # print(dataManipulationStruct.function, args)
        function = dataStruct.function
        return function(*args)

    @staticmethod
    def preprocessArguments(object, dataStruct):

        inputArgs = []
        # needed for eval of arguments as property names
        self = object
        for i in range(0, len(dataStruct.inputArguments)):
            if (dataStruct.inputArguments[i] is not None):
                if (dataStruct.inputArguments[i][0:5] == 'self.'):
                    if not object:
                        raise ValueError('self reference can only be used for data manipulation methods, not functions')
                    temp = eval(dataStruct.inputArguments[i])
                    if isinstance(temp, list):
                        inputArgs = inputArgs + temp
                    elif temp is not None:
                        inputArgs.append(temp)
                else:
                    inputArgs.append(dataStruct.inputArguments[i])

        outputArgs = []
        for i in range(0, len(dataStruct.outputArguments)):
            if (dataStruct.outputArguments[i] is not None):
                if (dataStruct.outputArguments[i][0:5] == 'self.'):
                    if not object:
                        raise ValueError('self reference can only be used for data manipulation methods, not functions')

                    temp = eval(dataStruct.outputArguments[i])
                    if isinstance(temp, list):
                        outputArgs = outputArgs + temp
                    elif temp is not None:
                        outputArgs.append(temp)
                else:
                    outputArgs.append(dataStruct.outputArguments[i])

        if (object):
            dataStruct.outputArguments = object.imposeSuffix(outputArgs)
            dataStruct.inputArguments = object.imposeSuffix(inputArgs)
        else:
            dataStruct.outputArguments = outputArgs
            dataStruct.inputArguments = inputArgs



        if not dataStruct.inputArguments and not dataStruct.takesData:
            dataStruct.takesNumElements = True

        if dataStruct.outputArguments:
            dataStruct.depthEntry = dataStruct.outputArguments[0]
        elif len(dataStruct.inputArguments) != 0:
            dataStruct.depthEntry = dataStruct.inputArguments[0]

    def getWrapperFunction(self, isMethod = True):
        dataStruct = self.dataStruct

        if isMethod:
            def data_function( object, data, indices=Ellipsis, registerOutput=True):

                functionName = dataStruct.function.__name__

                if not hasattr(object, 'dataManipulation_' + functionName):

                    newDataStruct = copy.copy(dataStruct)
                    newDataStruct.function = getattr(object, functionName)

                    self.preprocessArguments(object, newDataStruct)

                    setattr(object, 'dataManipulation_' + functionName, newDataStruct)
                else:
                    newDataStruct = getattr(object, 'dataManipulation_' + functionName)

                output = _DataDecorator._callDataFunctionInternal(object, newDataStruct, data, indices, registerOutput)
                return output
        else:
            def data_function(data, indices=Ellipsis, registerOutput=True):

                if not dataStruct.isInitialized:
                    dataStruct.isInitialized = True

                    self.preprocessArguments(None, dataStruct )
                    # If we are currently using a suffix stack for the names, impose the suffix to all data entries if we can
                    # find the name with the suffix. Suffix imposement can be avoided by manually putting "NoSuffix" as a suffix.
                    # The "NoSuffix" string will be deleted.

                output = _DataDecorator._callDataFunctionInternal(None, dataStruct, data, indices, registerOutput)
                return output

        return data_function


class ManipulatorMetaClass(type):
    def __init__(cls, name, bases, dct):

        super(ManipulatorMetaClass, cls).__init__(name, bases, dct)

        cloneDict = cls.__dict__.copy()
        for (key, function) in cloneDict.items():

            if hasattr(function, 'dataFunctionDecorator'):
                name = function.__name__

                decorator = function.dataFunctionDecorator
                newFunction = decorator.getWrapperFunction(function)

                setattr(cls, name + '_fromData', newFunction)

                function.dataFunction = newFunction
                setattr(cls, name, function)




class DataManipulator(SettingsClient, metaclass=ManipulatorMetaClass):
    '''
    TODO: update the class description with decorators

    The DataManipulator class defines the interfaces for manipulating the
    data structure. Hence this is the base class for almost all classes
    that interact with the data. It also stores the data manager for the
    highest hierarchy level such that we can access the properties of the
    data.

    Data manipulation functions

    Every DataManipulator can publish its data-manipulation functions.
    For each data manipulation function, we have to specify the input and the
    output data entries.
    If we call function with the data manipulation interface
    (DataManipulator.callDataFunction),
    the input arguments get automatically parsed out of the data structure and
    are put in as matrices for the function call.
    The output arguments of the function are also automatically stored back in
    the data structure. Almost every object that is supposed to change a data
    object is implemented as DataManipulator.
    This includes sampling episodes from different envs, policies,
    learned forward models or reward functions. Data manipulation functions
    can also obtain the number of elements that need to be processed as the
    first argument of the call of the function.
    This is in particularly useful if no other input arguments are specified
    (for example, for sampling initial states). whether or not a specific data
    manipulation function get the number of elements as input can be specified
    by a flag when publishing the function (addDataManipulationFunction).

    Call modes for Data manipulation functions

    Data manipulation functions can be called in three different modes.
    The modes are defined in DataFunctionType and can have the values
     - SINGLE_SAMPLE: The data manipulation function is called for each
     data point individually (with a for loop).
     - ALL_AT_ONCE: The data manipulation function is called for all data
     elements at once (in matrix form)
     - PER_EPISODE: The data function is called for all data elements
     that belong to one episode (i.e. are on the hierarchy level 2).

    Calling data manipulation functions

    The data manipulation functions can be called with
    callDataFunction or callDataFunctionOutput. The first one also
    stores the output of the function already in the data structure
    (note: the output arguments need to be registered in the data manager
    for that!). With callDataFunctionOutput the output of the data
    manipulation function is returned as for standard functions. When
    calling a data manipulation function we can also use the standard
    hierarchical indicing that we know from the Data class. Hence, the
    data manipulation functions can be applied to only a subset of the
    elements of a data object.

    DataManipulation function aliases

    We can also define aliases for data manipulation functions. An alias
    can point to a single data manipulation function (hence, it serves as
    a different name for the same data manipulation function), or it can
    also represent a sequence of data manipulation functions. Please see
    the function addDataFunctionAlias and the test scripts.
    '''

    @staticmethod
    def DataFunction(function):
        function.dataFunction = function
        return function

    @staticmethod
    def DataManipulationMethod(inputArguments, outputArguments, callType=CallType.ALL_AT_ONCE, takesNumElements=False, takesData = False):

            def wrapper(function):

                decorator = _DataDecorator(function, inputArguments, outputArguments, callType, takesNumElements, takesData)
                function.dataFunctionDecorator = decorator
                return function

            return wrapper



    def __init__(self, dataManager):
        '''
        Constructor
        '''
        if not isinstance(dataManager, DataManager):
            raise ValueError("dataManager has to be of type DataManager, not " +
                             str(type(dataManager)))
        super().__init__()
        self.dataManager = dataManager

    def imposeSuffix(self, argumentList):
        for i in range(0, len(argumentList)):
            name = argumentList[i]
            if len(name) > 8 and name[-8:] == 'NoSuffix':
                name = name[0:-8]
            else:
                nameWithSuffix = self.getNameWithSuffix(name)
                if self.dataManager.isDataEntry(nameWithSuffix):
                    name = nameWithSuffix

            argumentList[i] = name
        return argumentList

