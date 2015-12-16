'''
Created on Dec 7, 2015

@author: Sebastian Kreutzer
'''

from DataManager import DataManager
from interfaces import DataManipulatorInterface
from enum import Enum
import numpy as np

CallType = Enum('CallType', 'SINGLE_SAMPLE ALL_AT_ONCE PER_EPISODE')


class DataManipulationFunction(object):
    '''
    Represents a data manipulation function used in the DataManipulator class.
    '''

    def __init__(self, function, inputArguments, outputArguments, depthEntry, indices,
                 takesNumElements, callType):
        '''
        Constructor
        '''
        self.function = function
        self.inputArguments = inputArguments
        self.outputArguments = outputArguments
        self.depthEntry = depthEntry
        self.indices = indices
        self.callType = callType
        self.takesNumElements = takesNumElements

    def __str__(self):
        return "%s: %s -> %s" % (self.function.__name__, self.inputArguments,
                                 self.outputArguments)


class DataManipulator(DataManipulatorInterface):
    '''
    The DataManipulator class defines the interfaces for manipulating the
    data structure. Hence this is the base class for almost all classes
    that interact with the data. It also stores the data manager for the
    highest hierarchy level such that we can access the properties of the
    data.

    @section datamanipulation_function Data manipulation functions
    Every DataManipulator can publish its data-manipulation functions.
    For each data manipulation function, we have to specify the input and the
    output data entries.
    If we call a function with the data manipulation interface
    (DataManipulator.callDataFunction),
    the input arguments get automatically parsed out of the data structure and
    are put in as matrices for the function call.
    The output arguments of the function are also automatically stored back in
    the data structure. Almost every object that is supposed to change a data
    object is implemented as DataManipulator.
    This includes sampling episodes from different environments, policies,
    learned forward models or reward functions. Data manipulation functions
    can also obtain the number of elements that need to be processed as the
    first argument of the call of the function.
    This is in particularly useful if no other input arguments are specified
    (for example, for sampling initial states). whether or not a specific data
    manipulation function get the number of elements as input can be specified
    by a flag when publishing the function (addDataManipulationFunction).

    @subsection datamanipulation_call_modes Call modes for DataManipulation functions
    Data manipulation functions can be called in three different modes.
    The modes are defined in DataFunctionType and can have the values
     - SINGLE_SAMPLE: The data manipulation function is called for each
     data point individually (with a for loop).
     - ALL_AT_ONCE: The data manipulation function is called for all data
     elements at once (in matrix form)
     - PER_EPISODE: The data function is called for all data elements
     that belong to one episode (i.e. are on the hierarchy level 2).

    @subsection datamanipulation_calling Calling data manipulation functions
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

    @section datamanipulation_additionalparameters DataManipulation function aliases
    We can also define aliases for data manipulation functions. An alias
    can point to a single data manipulation function (hence, it serves as
    a different name for the same data manipulation function), or it can
    also represent a sequence of data manipulation functions. Please see
    the function addDataFunctionAlias and the test scripts.
    '''

    def __init__(self, dataManager):
        '''
        Constructor
        '''
        if not isinstance(dataManager, DataManager):
            raise ValueError("dataManager has to be a DataManager")
        self._dataManager = dataManager
        self._samplerFunctions = {}
        self._manipulationFunctions = {}

    def addDataFunctionAlias(self, aliasName, functionName, pushToFront=False):
        '''
        Adds a function alias. A function alias is just a different
        name for the same function. Can be used if certain samplers
        require a specific data manipulation function that is not
        directly implemented by the class, but there is another
        function with the same functionality. For example,
        used by learned distributions that are used as model or
        policy. In this case, we can tell the data manipulator that
        instead of the function sampleAction, we can use
        sampleFromDistribution. We can also use a data function alias to call
        several data manipulation function sequentially. If a data
        function alias has already been registered, the functionName
        is extended to the cell array of functionNames for that
        sampler function. If the sampler function is called, all
        registered data manipulation function for that sampler are
        called sequentially. We can also specify an external sampler
        in case we want to call a data manipulation function of
        another class.
        '''
        if functionName not in self._manipulationFunctions:
            raise ValueError("Manipulation function is not defined")

        if aliasName in self._samplerFunctions:
            functionList = self._samplerFunctions[aliasName]
            if pushToFront:
                functionList.insert(0, functionName)
            else:
                functionList.append(functionName)
        else:
            self._samplerFunctions[aliasName] = [functionName]

    def clearDataFunctionAlias(self, alias):
        del self._samplerFunctions[alias]

    def addDataManipulationFunction(self, function, inputArguments,
                                    outputArguments,
                                    callType=CallType.ALL_AT_ONCE,
                                    takesNumElements=False):
        if not inputArguments:
            takesNumElements = True

        if not isinstance(inputArguments, list):
            inputArguments = [inputArguments]

        if not isinstance(outputArguments, list):
            outputArguments = [outputArguments]

        depthEntry = ''
        if outputArguments:
            depthEntry = outputArguments[0]
        else:
            for inputArg in inputArguments:
                if inputArg:
                    depthEntry = inputArg
                    break

        indices = [] # FIXME: ??

        dmf = DataManipulationFunction(function, inputArguments,
                                       outputArguments, depthEntry,
                                       indices, takesNumElements, callType)
        self._manipulationFunctions[function.__name__] = dmf

        if function.__name__ in self._samplerFunctions:
            del self._samplerFunctions[function.__name__]
        self.addDataFunctionAlias(function.__name__, function.__name__)

    def callDataFunction(self, samplerName, data, indices):
        if samplerName not in self._samplerFunctions:
            raise ValueError("Data function %s is not defined" % samplerName)
        functionNames = self._samplerFunctions[samplerName]
        for functionName in functionNames:
            dmf = self._manipulationFunctions[functionName]
            self._callDataFunctionInternal(dmf, data, True, indices)

    def _callDataFunctionInternal(self, dataManipulationStruct, data,
                                  registerOutput, indices):
        '''
        Calls the data function using the right call type.
        If registerOutput is set, the resulting data will be written back
        into the object.
        '''
        callData = True

        if dataManipulationStruct.callType is CallType.PER_EPISODE:
            indices = data.completeLayerIndex(2, indices)  # TODO: Not implemented yet

        if dataManipulationStruct.callType is CallType.SINGLE_SAMPLE or \
                dataManipulationStruct.callType is CallType.PER_EPISODE:
            outArgs = None
            numLayers = len(indices)
            if dataManipulationStruct.callType is CallType.PER_EPISODE:
                numLayers = 1
            for i in range(0, numLayers):
                # This is somewhat hacky
                indexRange = range(0, indices[i].stop)[indices[i]]
                if len(indexRange) > 1:
                    callData = False
                    for j in indexRange:
                        indicesSingle = indices
                        indicesSingle[i] = slice(j, j+1)
                        if registerOutput:
                            self._callDataFunctionInternal(
                                dataManipulationStruct,
                                data,
                                registerOutput,
                                indicesSingle)
                        else:
                            tempOut = self._callDataFunctionInternal(
                                    dataManipulationStruct,
                                    data,
                                    registerOutput,
                                    indicesSingle)
                            if outArgs is None:
                                outArgs = tempOut
                            else:
                                outArgs = np.vstack((outArgs, tempOut))
            # Do something here with outArgs
            return outArgs

        if callData:
            inputArgs = data.getDataEntryList(
                            dataManipulationStruct.inputArguments, indices)

            for i, arg in enumerate(inputArgs):
                inputArgs[i] = arg # TODO: Select columns based on indices
                
            if dataManipulationStruct.takesNumElements:
                outputDepth = self._dataManager.getDataEntryDepth(dataManipulationStruct.depthEntry)
                numElements = data.getNumElementsForIndex(outputDepth, indices)

            outArgs = self._callDataFuntionInternalMatrices(
                            dataManipulationStruct, data, numElements, inputArgs)
            if registerOutput:
                data.setDataEntryList(dataManipulationStruct.outputArguments,
                                      indices, outArgs)

            return outArgs

    def _callDataFuntionInternalMatrices(self, dataManipulationStruct,
                                         data, numElements, inputArgs):
        '''
        Directly calls the manipulation function and returns the result matrix.
        '''
        # It is here assumed that the sampler function doesn't take data.
        # Not sure where this would be useful?
        if inputArgs:
            result = self._unpackAndInvoke(dataManipulationStruct.function, numElements, inputArgs)
        else:
            result = self._unpackAndInvoke(dataManipulationStruct.function, numElements)
        return result

    def _unpackAndInvoke(self, function, *args):
        print(*args)
        return function(*args)