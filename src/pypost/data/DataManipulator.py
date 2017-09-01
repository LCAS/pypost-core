from pypost.data.DataManager import DataManager
from pypost.common.SettingsClient import SettingsClient

import numpy as np
from enum import Enum

import copy

class CallType(Enum):
    SINGLE_SAMPLE = 1
    ALL_AT_ONCE = 2
    PER_EPISODE = 3




class DataManipulationFunction():
    '''
    Represents a data manipulation function used in the DataManipulator class.
    '''

    def __init__(self, name, inputArguments, outputArguments, callType = CallType.ALL_AT_ONCE, takesNumElements = False, takesData = False, lazyEvaluation = False):
        '''
        Constructor
        '''

        self.name = name
        self.inputArguments = inputArguments
        self.outputArguments = outputArguments
        self.takesData = takesData
        self.callType = callType
        self.takesNumElements = takesNumElements
        self.isInitialized = False
        self.depthEntry = None
        self.dataFunctionObject = None
        self.lazyEvaluation = lazyEvaluation

        if not isinstance(self.inputArguments, list):
            self.inputArguments = [self.inputArguments]

        if not isinstance(self.outputArguments, list):
            self.outputArguments = [self.outputArguments]

    def __str__(self):
        return "%s: %s -> %s" % (self.name, self.inputArguments,
                                 self.outputArguments)

    def listArguments(self):
        print(self.__str__())

    def _callDataFunctionInternal(self, function, data, indices, registerOutput):

        '''
        Calls the data function using the right call type.
        If registerOutput is set, the resulting data will be written back
        into the object.
        '''
        callData = True
        dataStruct = self

        if dataStruct.callType is CallType.PER_EPISODE:
            indices = data.completeLayerIndex(1, indices)
        elif dataStruct.callType is CallType.SINGLE_SAMPLE:
            indices = data.completeLayerIndex(
                data.dataManager.getDataEntryLevel(
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
                            indicesSingle[i] = j
                            if registerOutput:
                                self._callDataFunctionInternal(function, data, indicesSingle, registerOutput)
                            else:
                                tempOut = self._callDataFunctionInternal(function, data,
                                    registerOutput,
                                    indicesSingle)
                                if outArgs is None:
                                    outArgs = tempOut
                                else:
                                    for i in range(0, len(outArgs)):
                                        outArgs[i] = np.vstack((outArgs[i],
                                                                tempOut[i]))
                if isinstance(indices[i], list):
                    # This is somewhat hacky, but it works!
                    # Maybe clone data and get shape directly?

                    if len(indices[i]) > 1:
                        callData = False
                        for j in range(0, len(indices[i])):
                            indicesSingle = list(indices)
                            indicesSingle[i] = indices[i][j]
                            if registerOutput:
                                self._callDataFunctionInternal(function, data, indicesSingle, registerOutput)
                            else:
                                tempOut = self._callDataFunctionInternal(function, data,
                                    registerOutput,
                                    indicesSingle)
                                if outArgs is None:
                                    outArgs = tempOut
                                else:
                                    for i in range(0, len(outArgs)):
                                        outArgs[i] = np.vstack((outArgs[i],
                                                                tempOut[i]))


        if callData:

            if dataStruct.depthEntry:
                outputDepth = data.dataManager.getDataEntryLevel(dataStruct.depthEntry)
                numElements = data.getNumElementsForIndex(outputDepth, indices)
            else:
                numElements = 1

            inputArgs = data.getDataEntryList(dataStruct.inputArguments, indices)
            if (self.lazyEvaluation):
                validFlag = data.getDataEntry(self.outputArguments[0] + '_validFlag', indices)
                notValidFlag = np.where(~validFlag)[0]

                for i in range(0, len(inputArgs)):
                    if isinstance(inputArgs[i], np.ndarray):
                        inputArgs[i] = inputArgs[i][notValidFlag]
                numElements = len(notValidFlag)


            if (numElements > 0):
                outArgs = self._callDataFuntionInternalMatrices(function, data, numElements, inputArgs)

                if not isinstance(outArgs, list):  # pragma: no branch
                    outArgList = [outArgs]
                else:
                    outArgList = outArgs

            if self.lazyEvaluation:
                outArgsAll = data.getDataEntryList(dataStruct.outputArguments, indices)

                if (numElements > 0):
                    for i in range(0, len(outArgsAll)):
                        outArgsAll[i][notValidFlag] = outArgList[i]

                outArgList = outArgsAll
                validFlag[:] = True
                data.setDataEntry(self.outputArguments[0] + '_validFlag', indices, validFlag)

            if registerOutput:
                if (len(outArgList) < len(dataStruct.outputArguments) or not all(x is not None for x in outArgList[:len(dataStruct.outputArguments)]) ):
                    raise ValueError("Function {0} returns {1} values but must return {2} values which are not None".format(function.__name__, len(outArgList), len(dataStruct.outputArguments)))
                data.setDataEntryList(dataStruct.outputArguments, indices, outArgList)
                # try:
                #     data.setDataEntryList(dataStruct.outputArguments, indices, outArgList)
                # except ValueError as error:
                #     raise ValueError('Error when registering output arguments of function ' + function.__name__ +
                #                      ': ' + error.args[0] + '. Please check your output arguments!')
            outArgs = outArgList

        if (outArgs and len(outArgs) == 1):
            return outArgs[0]
        else:
            return outArgs

    def _callDataFuntionInternalMatrices(self, function, data, numElements, inputArgs):
        '''
        Directly calls the manipulation function and returns the result matrix.
        '''
        dataStruct = self
        args = []
        if dataStruct.takesNumElements:
            args.append(numElements)
        if dataStruct.takesData:
            args.append(data)

        args.extend(inputArgs)
        args = tuple(args)

        # print(dataManipulationStruct.function, args)
        return function(*args)

    def preprocessArguments(self):

        dataStruct = self
        object = self.dataFunctionObject
        inputArgs = []
        for i in range(0, len(dataStruct.inputArguments)):
            if (dataStruct.inputArguments[i] is not None):
                if (dataStruct.inputArguments[i][0:5] == 'self.'):
                    objString = dataStruct.inputArguments[i].replace('self.', 'object.')

                    preprocessorString = ''
                    if ('__' in objString):
                        indexUnderScore = objString.index('__')
                        if (indexUnderScore > 0):
                            preprocessorString = objString[indexUnderScore+2:]

                            objString = objString[:indexUnderScore]


                    if not object:
                        raise ValueError('self reference can only be used for data manipulation methods, not functions')

                    objStringTmp = objString.replace('object.', '')

                    if hasattr(object, objStringTmp):
                        temp = eval(objString)

                        if len(preprocessorString) > 0:
                            temp = temp + '__' + preprocessorString

                        if isinstance(temp, list):
                            inputArgs = inputArgs + temp
                        elif temp is not None:
                            inputArgs.append(temp)
                    else:
                        raise ValueError('self reference {} not found'.format(objStringTmp))

                else:
                    inputArgs.append(dataStruct.inputArguments[i])

        outputArgs = []
        for i in range(0, len(dataStruct.outputArguments)):
            if (dataStruct.outputArguments[i] is not None):
                if (dataStruct.outputArguments[i][0:5] == 'self.'):
                    objString = dataStruct.outputArguments[i].replace('self.', 'object.')
                    if not object:
                        raise ValueError('self reference can only be used for data manipulation methods, not functions')

                    temp = eval(objString)
                    if isinstance(temp, list):
                        outputArgs = outputArgs + temp
                    elif temp is not None:
                        outputArgs.append(temp)
                else:
                    outputArgs.append(dataStruct.outputArguments[i])

        if (object):
            dataStruct.outputArguments = object.imposeSuffix(outputArgs)
            dataStruct.inputArguments = object.imposeSuffix(inputArgs)
            # check data
            manager = object.dataManager

            manager.checkDataEntries(dataStruct.inputArguments, 'Function {} input arguments'.format(self.name))
            manager.checkDataEntries(dataStruct.outputArguments, 'Function {} input arguments'.format(self.name))

        else:
            dataStruct.outputArguments = outputArgs
            dataStruct.inputArguments = inputArgs



        #if not dataStruct.inputArguments and not dataStruct.takesData:
        #    dataStruct.takesNumElements = True

        if dataStruct.outputArguments:
            dataStruct.depthEntry = dataStruct.outputArguments[0]
        elif len(dataStruct.inputArguments) != 0:
            dataStruct.depthEntry = dataStruct.inputArguments[0]

        if dataStruct.depthEntry and '__' in dataStruct.depthEntry:
            index = dataStruct.depthEntry.find('__')
            dataStruct.depthEntry = dataStruct.depthEntry[0:index]

    def dataFunction(self, function, data, indices=Ellipsis, registerOutput=True):

        if hasattr(function, '__self__') and not self.dataFunctionObject:

            function.__self__.callData = data
            outArgs = function.__self__.dataManipulationMethodsInstance[function.__name__].dataFunction(function, data, indices, registerOutput)
            function.__self__.callData = None

            return outArgs
        else:
            if (not self.isInitialized):
                self.inialized = True
                self.preprocessArguments()

            output = self._callDataFunctionInternal(function, data, indices, registerOutput)
            return output



def DataFunction(inputArguments, outputArguments, callType = CallType.ALL_AT_ONCE, takesNumElements = False, takesData = False):
    def wrapper(function):
        if (hasattr(function, '__self__')):
            raise ValueError('For class methods, please use the DataManipulator.DataManipulationMethod decorator')

        function.dataFunctionDecorator = DataManipulationFunction(function.__name__, inputArguments, outputArguments, callType,
                                                takesNumElements, takesData)

        return function
    return wrapper



class ManipulatorMetaClass(type):
    def __init__(cls, name, bases, dct):

        super(ManipulatorMetaClass, cls).__init__(name, bases, dct)

        cloneDict = cls.__dict__.copy()
        for (key, function) in cloneDict.items():

            if (hasattr(function, '__name__')):
                name = function.__name__

                if (hasattr(function, 'dataFunctionDecorator')):
                    setattr(cls, name + '_dataDecorator', function.dataFunctionDecorator)

                if hasattr(cls, name + '_dataDecorator'):

                    function.dataFunctionDecorator = copy.deepcopy(getattr(cls, name + '_dataDecorator'))
                    setattr(cls, name, function)





                #if hasattr(cls, name + '_fromData'):
                #    dataFunction =  getattr(cls, name + '_fromData')
                #    newClass = createDataFunction(cls.__name__ + '__' + name, function, dataFunction)
                #    functionInstance = newClass()
                #    setattr(cls, name, functionInstance)

            #function.dataFunction = newFunction
                #setattr(function, '__le__', DataFunctionOperator)
                #setattr(cls, name, function)





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
    def DataMethod( inputArguments, outputArguments, callType=CallType.ALL_AT_ONCE, takesNumElements=False, takesData = False, lazyEvaluation = False):

            def wrapper(function):

                function.dataFunctionDecorator = DataManipulationFunction(function.__name__, inputArguments, outputArguments, callType, takesNumElements, takesData, lazyEvaluation)
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
        self.dataManipulationMethodsInstance = {}
        self.callData = None

        cloneDict = self.__dir__()
        for key in cloneDict:

            if key.endswith('_dataDecorator'):

                name = key[:-14]
                dataDecorator = copy.deepcopy(getattr(self, key))
                dataDecorator.dataFunctionObject = self

                self.dataManipulationMethodsInstance[name] = dataDecorator


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

    def listManipulationFunctions(self):
        for (functionName, decorator) in self.dataManipulationMethodsInstance.items():
            print('{} : {} -> {}'.format(functionName, decorator.inputArguments, decorator.outputArguments))

