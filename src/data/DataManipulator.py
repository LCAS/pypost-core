from data.DataManipulatorInterface import DataManipulatorInterface
from data.DataManipulatorInterface import CallType
from data.DataManager import DataManager
import numpy as np


class DataManipulationFunction():
    '''
    Represents a data manipulation function used in the DataManipulator class.
    '''

    def __init__(self, function, inputArguments, outputArguments, depthEntry,
                 indices, takesNumElements, callType):
        '''
        Constructor
        '''
        if not isinstance(depthEntry, str):
            raise ValueError("depthEntry has to be a string: ", depthEntry)

        self.function = function
        self.inputArguments = inputArguments
        self.outputArguments = outputArguments
        self.depthEntry = depthEntry
        self.indices = indices
        self.takesData = False
        self.callType = callType
        self.takesNumElements = takesNumElements

    def __str__(self):
        return "%s: %s -> %s\n   depthEntry: %s\n   indices: %s\n   takesData: %s\n   callType: %s\n   takesNumElements: %s\n" % (
                self.function.__name__, self.inputArguments,
                self.outputArguments, self.depthEntry, self.indices, self.takesData, self.callType, self.takesNumElements)

class DataManipulator(DataManipulatorInterface):
    '''
    TODO: update the class description

    The DataManipulator class defines the interfaces for manipulating the
    data structure. Hence this is the base class for almost all classes
    that interact with the data. It also stores the data manager for the
    highest hierarchy level such that we can access the properties of the
    data.

    Data manipulation functions

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
        '''
        Deletes the entry for the given alias name.
        '''
        del self._samplerFunctions[alias]

    def addDataManipulationFunction(self, function, inputArguments,
                                    outputArguments,
                                    callType=None,
                                    takesNumElements=None,
                                    name=None):
        '''
        Adds a new data manipulation function.
        :param function: The data manipulation function
        :param inputArguments: A list of input arguments (can also be a single
                               string)
        :param outputArguments: A list of output arguments (can also be a
                                single string)
        :param callType: One of the three different call types
        :param takesNumElements: Whether the function takes the number of
                                 elements as an input arguments
        :param name: The name of the function (default is the actual function
                     name)
        '''
        if isinstance(function, str):
            raise ValueError('The function parameter must not be a string: ',
                             function)

        if callType is None:
            callType = CallType.ALL_AT_ONCE

        if takesNumElements is None:
            takesNumElements = False

        if name is None:
            name = function.__name__

        if not inputArguments:
            takesNumElements = True

        if not isinstance(inputArguments, list):
            inputArguments = [inputArguments]

        if not isinstance(outputArguments, list):
            outputArguments = [outputArguments]

        depthEntry = ''
        if outputArguments:
            depthEntry = outputArguments[0]
        elif len(inputArguments) != 0:
            depthEntry = inputArguments[0]

        # A None entry indicates that the whole entry should be used
        indices = [None] * len(inputArguments)

        dmf = DataManipulationFunction(function, inputArguments,
                                       outputArguments, depthEntry,
                                       indices, takesNumElements, callType)
        self._manipulationFunctions[name] = dmf

        if name in self._samplerFunctions:
            del self._samplerFunctions[name]
        self.addDataFunctionAlias(name, name)

    def isSamplerFunction(self, samplerName):
        '''
        Checks if the given function name is defined.
        :param samplerName: The function name
        :return: True if the function is defined, False otherwise
        :rtype: bool
        '''
        return samplerName in self._samplerFunctions

    def setIndices(self, name, numInput, indices):
        '''
        Sets the indices of the data used as input for the given function.
        :param name: The function name
        :param numInput: The index of the function arguments
        :param indices: The selected indices
        '''
        if name not in self._manipulationFunctions:
            raise ValueError("Data function %s is not defined" % name)
        dataFunction = self._manipulationFunctions[name]
        if len(dataFunction.inputArguments) <= numInput:
            raise ValueError("Input argument of index %d is not defined" %
                             numInput)
        dataFunction.indices[numInput] = indices

    def setTakesData(self, name, takesData):
        '''
        Sets whether the given function takes a data object as input.
        :param name: The function name
        :param takesData: If true, the function will be called with a data
                          object as input
        '''
        if name not in self._manipulationFunctions:
            raise ValueError("Data function %s is not defined" % name)
        self._manipulationFunctions[name].takesData = takesData

    def callDataFunction(self, samplerName, data, indices):
        '''
        Calls a data function with the given indices.
        Writes the result back into the data object.
        :param samplerName: The name of the function
        :param data: The data object
        :param indices: The indices that will be selected from the data object
                        as input for the function.
        '''
        if samplerName not in self._samplerFunctions:
            raise ValueError("Data function %s is not defined" % samplerName)
        functionNames = self._samplerFunctions[samplerName]
        for functionName in functionNames:
            dmf = self._manipulationFunctions[functionName]
            self._callDataFunctionInternal(dmf, data, True, indices)

    def callDataFunctionOutput(self, samplerName, data, indices):
        '''
        Calls a data function with the given indices.
        Returns the results back to the caller.
        :param samplerName: The name of the function
        :param data: The data object
        :param indices: The indices that will be selected from the data object
                        as input for the function.
        :return: The output data of the called function.
        '''
        if samplerName not in self._samplerFunctions:
            raise ValueError("Data function %s is not defined" % samplerName)
        functionNames = self._samplerFunctions[samplerName]
        output = []
        for functionName in functionNames:
            dmf = self._manipulationFunctions[functionName]
            output.append(self._callDataFunctionInternal(dmf, data, False,
                                                         indices))
        return output

    def _callDataFunctionInternal(self, dataManipulationStruct, data,
                                  registerOutput, indices):
        '''
        Calls the data function using the right call type.
        If registerOutput is set, the resulting data will be written back
        into the object.
        '''
        callData = True

        if dataManipulationStruct.callType is CallType.PER_EPISODE:
            indices = data.completeLayerIndex(1, indices)
        elif dataManipulationStruct.callType is CallType.SINGLE_SAMPLE:
            for i in range(0, len(indices)):
                if not isinstance(indices[i], int):
                    raise ValueError("SINGLE_SAMPLE functions cannot be called"
                                     " with multiple input values")
            indices = data.completeLayerIndex(
                data.dataManager.getDataEntryDepth(
                    dataManipulationStruct.depthEntry), indices)

        if dataManipulationStruct.callType is CallType.SINGLE_SAMPLE or \
                dataManipulationStruct.callType is CallType.PER_EPISODE:
            outArgs = None
            numLayers = len(indices)
            if dataManipulationStruct.callType is CallType.PER_EPISODE:
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
                                    for i in range(0, len(outArgs)):
                                        outArgs[i] = np.vstack((outArgs[i],
                                                                tempOut[i]))

        if callData:
            inputArgs = data.getDataEntryList(
                dataManipulationStruct.inputArguments, indices)

            # Select columns according to given indices
            for i, arg in enumerate(inputArgs):
                if dataManipulationStruct.indices[i] is not None:
                    inputArgs[i] = arg[:, dataManipulationStruct.indices[i]]

            numElements = None
            if dataManipulationStruct.takesNumElements:
                outputDepth = self._dataManager.getDataEntryDepth(
                    dataManipulationStruct.depthEntry)
                numElements = data.getNumElementsForIndex(outputDepth, indices)

            outArgs = self._callDataFuntionInternalMatrices(
                dataManipulationStruct, data, numElements,
                inputArgs)

            if not isinstance(outArgs, list): # pragma: no branch
                outArgs = [outArgs]

            if registerOutput:
                data.setDataEntryList(dataManipulationStruct.outputArguments,
                                      indices, outArgs)

        return outArgs

    def _callDataFuntionInternalMatrices(self, dataManipulationStruct,
                                         data, numElements, inputArgs):
        '''
        Directly calls the manipulation function and returns the result matrix.
        '''
        args = []
        if dataManipulationStruct.takesNumElements:
            args.append(numElements)
        if dataManipulationStruct.takesData:
            args.append(data)
        if inputArgs is not None:
            args.extend(inputArgs)
        args = tuple(args)

        return dataManipulationStruct.function(*args)
