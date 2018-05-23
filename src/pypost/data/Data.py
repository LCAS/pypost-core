import numpy as np
import tensorflow as tf
from pypost.data.DataStructure import DataStructure


class DataEntryInfo():
    '''
    Stores meta data about entries and aliases.
    '''

    def __init__(self, depth, entryList, numDimensions,
                 minRange, maxRange, isFeature = False, callBackGetter = None):
        """Constructor for DataEntryInfo

        :param depth: The depth in which the DataEntryInfo resides within the
                      data structure.
        :param entryList: The entry list of the data entry.
        :param numDimensions: The dimensions of the data entry.
        :param minRange: The minimum values of the data entry
        :param maxRange: The maximum values of the data entry
        """
        self.depth = depth
        self.entryList = entryList
        self.numDimensions = numDimensions
        self.minRange = minRange
        self.maxRange = maxRange
        self.isFeature = isFeature
        self.callBackGetter = callBackGetter


class Data(object):


    class FlatIndex():

        def __init__(self, flatIndex):
            self.flatIndex = flatIndex

    '''
    Stores meta data for each data entry to make access simple and fast.
    '''

    def __init__(self, dataManager, dataStructure):
        '''
        Constructor
        '''
        self.entryInfoMap = {}
        self.dataManager = dataManager
        self.dataStructure = dataStructure

        self.activeIndex = (Ellipsis,)
        self.isFlatIndex = False
        # create the entryInfoMap

        aliasNames = self.dataManager.getAliasNames()
        entryNames = self.dataManager.getEntryNames()

        self.tensorDictionary = {}
        for name in aliasNames:
            depth = self.dataManager.getDataEntryLevel(name)
            alias = self.dataManager.getDataAlias(name)
            self.entryInfoMap[name] = \
                DataEntryInfo(depth, alias.entryList, alias.numDimensions,
                              self.dataManager.getMinRange(name),
                              self.dataManager.getMaxRange(name))

            if name in entryNames:
                entry = self.dataManager.getDataEntry(name)
                self.entryInfoMap[name].isFeature = entry.isFeature
                self.entryInfoMap[name].callBackGetter = entry.callBackGetter


            setattr(self, name, None)

    def __getstate__(self):
        dictState = {}
        dictState['dataManager'] = self.dataManager
        dictState['dataStructure'] = self.dataStructure
        dictState['isFlatIndex'] = self.isFlatIndex
        return dictState

    def __setstate__(self, state):
        from pypost.data import DataManager

        self.entryInfoMap = {}

        self.dataManager = state['dataManager']

        aliasNames = self.dataManager.getAliasNames()
        entryNames = self.dataManager.getEntryNames()

        self.dataStructure = state['dataStructure']
        self.activeIndex = (Ellipsis,)
        self.isFlatIndex = state['isFlatIndex']

        self.tensorDictionary = {}
        for name in aliasNames:
            depth = self.dataManager.getDataEntryLevel(name)
            alias = self.dataManager.getDataAlias(name)
            self.entryInfoMap[name] = \
                DataEntryInfo(depth, alias.entryList, alias.numDimensions,
                              self.dataManager.getMinRange(name),
                              self.dataManager.getMaxRange(name))

            if name in entryNames:
                entry = self.dataManager.getDataEntry(name)
                self.entryInfoMap[name].isFeature = entry.isFeature
                self.entryInfoMap[name].callBackGetter = entry.callBackGetter

            setattr(self, name, None)

    def clone(self):
        import pickle

        newData = self.dataManager.createDataObject(0)
        b = pickle.dumps(self.dataStructure)
        newData.dataStructure = pickle.loads(b)

        return newData

    def getDataManager(self):
        return self.dataManager

    def _addTensorToDictionary(self, tensor):
        from pypost.mappings import TFMapping
        tensorMapping = TFMapping(self.dataManager, tensorNode=tensor, name='data_tfmapping')
        self.tensorDictionary[tensor] = tensorMapping
        return tensorMapping

    def _getTensorMappingForTensor(self, tensor):

        if tensor in self.tensorDictionary:
            return self.tensorDictionary[tensor]
        else:
            return self._addTensorToDictionary(tensor)


    def _createDataStructure(self, dataManager, numElements):
        '''
        Creates the data structure (containing real data) for the data object.

        :param numElements: A vector defining the number of elements for each
                           layer of the hierarchy.
                           This parameter may also be an integer, in which case
                           all layers will have the same number of data points.
        :return: The newly created data structure
        :rtype: data.DataStructure
        '''
        if isinstance(numElements, list):
            numElementsCurrentLayer = numElements[0]
            numElements = numElements[1:]
        else:
            numElementsCurrentLayer = numElements

        dataStructure = DataStructure(self, numElementsCurrentLayer, dataManager.isTimeSeries)
        for dataEntryName, dataEntry in dataManager.dataEntries.items():
            dataStructure.createEntry(dataEntryName, dataEntry)

        for dataAliasName, dataAlias in dataManager.dataAliases.items():
            if dataAliasName not in dataManager.dataEntries:
                dataStructure.createAlias(dataAliasName, dataAlias)

        if (dataManager.subDataManager is not None):
            subDataStructures = []

            for _ in range(0, numElementsCurrentLayer):
                subDS = self._createDataStructure(dataManager.subDataManager, numElements)
                subDataStructures.append(subDS)

            dataStructure.createAliasSubDataStructure(dataManager.subDataManager.name, subDataStructures)

        return dataStructure

    def __getitem__(self, index):
        return DataView(self, index)

    def __setattr__(self, name, value):
        indexPreprocessor = name.find('__')
        if indexPreprocessor > 0:
            nameEntry = name[:indexPreprocessor]
        else:
            nameEntry = name
        if (value is not None and name != 'entryInfoMap' and nameEntry in self.entryInfoMap):
            index = self.activeIndex
            if (isinstance(index, tuple)):
                index = list(index)

            if self.isFlatIndex:
                return self.setDataEntryFlat(name, index, value)
            else:
                return self.setDataEntry(name, index, value)
        else:
            return super().__setattr__(name, value)

    def __getattribute__(self, name):

        indexPreprocessor = name.find('__')
        if indexPreprocessor > 0:
            nameEntry = name[:indexPreprocessor]
        else:
            nameEntry = name


        if (name != 'entryInfoMap' and hasattr(self, 'entryInfoMap') and nameEntry in self.entryInfoMap):
            index = self.activeIndex
            if (isinstance(index, tuple)):
                index = list(index)

            if (not self.isFlatIndex):
                return self.getDataEntry(name, index)
            else:
                return self.getDataEntryFlat(name, index)
        else:
            return super().__getattribute__(name)

    def apply(self, function):
        if (isinstance(function, (tf.Tensor, tf.Variable)) or (isinstance(function, tuple) and all(isinstance(x, (tf.Tensor, tf.Variable)) for x in function))):
            function = self._getTensorMappingForTensor(function)

        if hasattr(function, '__call__') and hasattr(function, 'dataFunctionDecorator'):
            function.dataFunctionDecorator.dataFunction(function, self, self.activeIndex, registerOutput = True)
            function.dataFunctionDecorator.dataWriter.apply(self)
            return self
        else:
            raise ValueError('Operator >> / apply can only be applied to manipulation functions or tuples of manipulation functions'
                             'and index')

    def applyReturn(self, function):
        if (isinstance(function, (tf.Tensor, tf.Variable)) or (
            isinstance(function, tuple) and all(isinstance(x, (tf.Tensor, tf.Variable)) for x in function))):

            function = self._getTensorMappingForTensor(function)

        if hasattr(function, '__call__') and hasattr(function, 'dataFunctionDecorator'):

            function.dataFunctionDecorator.dataFunction(function, self, self.activeIndex, registerOutput = True)

            return function.dataFunctionDecorator.dataWriter.apply(self)
        else:
            raise ValueError('Operator >= / applyReturn can only be applied to manipulation functions or tuples of manipulation functions'
                             'and index')

    def applyNoWrite(self, function):
        if (isinstance(function, (tf.Tensor, tf.Variable)) or (isinstance(function, tuple) and all(isinstance(x, (tf.Tensor, tf.Variable)) for x in function))):
            function = self._getTensorMappingForTensor(function)

        if hasattr(function, '__call__') and hasattr(function, 'dataFunctionDecorator'):
            return function.dataFunctionDecorator.dataFunction(function, self, (self.activeIndex), registerOutput=False)

        else:
            raise ValueError(
                'Operator > / applyNoWrite can only be applied to manipulation functions or tuples of manipulation functions'
                'and index')

    def __rshift__(self, function):
        '''Operator for applying data manipulation functions'''
        if (isinstance(function, (tf.Tensor, tf.Variable, tf.Operation)) or (isinstance(function, tuple) and all(isinstance(x, (tf.Tensor, tf.Variable, tf.Operation)) for x in function))):
            function = self._getTensorMappingForTensor(function)

        if hasattr(function, '__call__') and hasattr(function, 'dataFunctionDecorator'):
            function.dataFunctionDecorator.dataFunction(function, self, self.activeIndex, registerOutput = True)
            return function.dataFunctionDecorator.dataWriter
        else:
            raise ValueError('Operator >> can only be applied to manipulation functions or tuples of manipulation functions'
                             'and index')



    def __rrshift__(self, function):


        if (isinstance(function, (tf.Tensor, tf.Variable)) or (
            isinstance(function, tuple) and all(isinstance(x, (tf.Tensor, tf.Variable)) for x in function))):
            function = self._getTensorMappingForTensor(function)

        if isinstance(function, DataWriter):
            dataWriter = function
            dataWriter.apply(self)
            return self
        elif (hasattr(function, '__call__') and hasattr(function, 'dataFunctionDecorator')):
            if len(function.dataFunctionDecorator.inputArguments) > 0:
                raise ValueError('Operator >> can only be applied on rhs to data if lhs is the output of a mapping operation (using >>) or directly to a mapping if the mapping does not get any data entry as input')
            else:
                self.apply(function)
                return self

    def __le__(self, function):

        if (isinstance(function, (tf.Tensor, tf.Variable)) or (
                    isinstance(function, tuple) and all(isinstance(x, (tf.Tensor, tf.Variable)) for x in function))):
            function = self._getTensorMappingForTensor(function)

        if isinstance(function, DataWriter):
            dataWriter = function
            return dataWriter.apply(self)
        elif (hasattr(function, '__call__') and hasattr(function, 'dataFunctionDecorator')):
            if len(function.dataFunctionDecorator.inputArguments) > 0:
                raise ValueError(
                    'Operator >> can only be applied on rhs to data if lhs is the output of a mapping operation (using >>) or directly to a mapping if the mapping does not get any data entry as input')
            else:
                return self.apply(function)

    def __ge__(self, function):
        '''Operator for applying data manipulation functions'''
        return self.applyNoWrite(function)

    def __lt__(self, function):
        if (hasattr(function, 'linkedDataEnties') and function.linkedDataEnties):
            function.writeDataPropertiesToData(self, self.activeIndex)

    def __gt__(self, function):
        if (hasattr(function, 'linkedDataEnties') and function.linkedDataEnties):
            function.readDataPropertiesFromData(self, self.activeIndex)


    def completeLayerIndex(self, depth, indices):
        '''This function completes the hierarchical indicing for the internal
        functions for accessing the data. E.g., if not enough indices are
        specified, it appends appropriate slices.

        :param depth: The depth of the indices path
        :param indices: The (potentially incomplete) indices
        :returns: The complete indices array
        '''
        if not isinstance(indices, list):
            if isinstance(indices, tuple):
                indices = list(indices)
            else:
                indices = [indices]

        while len(indices) <= depth:
            indices.append(...)
        if len(indices) > depth + 1:
            indices = indices[0:depth+1]

        manager = self.dataManager
        dataStructure = self.dataStructure

        for i in range(0, len(indices)):
            if indices[i] == Ellipsis:
                indices[i] = slice(0, dataStructure.numElements)
            manager = manager.subDataManager
            if manager is not None:
                dataStructure = dataStructure.nextLayer[0]
        return indices

    def getNumElements(self, entryName=None):
        '''
        Returns the number of elements for the given data entry.
        (depends on the hierarchy level of the entry).
        '''
        depth = 0
        if entryName is not None:
            depth = self.entryInfoMap[entryName].depth
        return self.getNumElementsForDepth(depth)

    def getNumElementsForDepth(self, depth):
        '''
        Returns the number of elements for the given depth of
        the hierarchy.
        '''
        return self.getNumElementsForIndex(depth, [])

    def getNumElementsForIndex(self, depth, indices=[]):
        if not isinstance(indices, list):
            if isinstance(indices, tuple):
                indices = list(indices)
            else:
                indices = [indices]


        while len(indices) <= depth:
            indices.append(...)

        return self.dataStructure.getNumElementsForIndex(depth, indices)

    def _resolveEntryPath(self, name):
        path = []

        index = name.find('__')
        if index > 0:
            nameDepth = name[:index]
        else:
            nameDepth = name

        depth = self.entryInfoMap[nameDepth].depth
        dataManager = self.dataManager.subDataManager
        while dataManager is not None and depth > 0:
            path.append(dataManager.name)
            dataManager = dataManager.subDataManager
            depth -= 1
        path.append(name)
        return path

    def resolveSuffixPath(self, path):

        index = path.find('__')
        if index < 0:
            return (path, '')
        else:
            return (path[:index], path[index + 1:])

    def callBackGetter(self, entryName, indices):

        index = entryName.find('__')
        if index > 0:
            entryName = entryName[:index]

        dataEntryInfo = self.entryInfoMap[entryName]
        if (dataEntryInfo.callBackGetter):
            callBack = dataEntryInfo.callBackGetter
            dataEntryInfo.callBackGetter = None
            self[tuple(indices)] >> callBack >> self
            dataEntryInfo.callBackGetter = callBack

        for entry in dataEntryInfo.entryList:
            if (entry[0] != entryName):
                self.callBackGetter(entry[0], indices)

    def getDataEntryFlat(self, path, flatIndex):
        
        data = self.getDataEntry(path, ...)
        return data[flatIndex[0], :]

    def setDataEntryFlat(self, path, flatIndex, dataNew):

        data = self.getDataEntry(path, ...)
        data[flatIndex,:] = dataNew
        self.setDataEntry(path, ..., data)

        return


    def getDataEntry(self, path, indices=[], cloneData=True, hStack = False):
        '''
        Returns the data points from the required data entry (or alias).

        :param path: the path to the requested entry as an array e.g.
                     ['steps', 'subSteps', 'subActions'] or simply the name of
                     the entry.
        :param indices: the hierarchical indices (depending on the hierarchy, it
                        can have different number of elements) as an array.
                        If this parameter is omitted or the number of indices is
                        less than the depth of the hierarchy (less than the
                        length of the path), all other indices will be treated
                        as "...".
                        indices may also be a number which is equivalent to an
                        array containing only one element
        :param cloneData: If true, a copy of the data will be returned. When
                          `cloneData` is False, modifying the returned data may
                          already impact the values stored in the data structure
                          which improves performance. In any case, it is crucial
                          to write all pending changes by using
                          :func:`setDataEntry`.
        :returns: the requested data
        '''
        #path, procDataStructure = self.resolveSuffixPath(path)

        if isinstance(path, list):
            entryName = path[-1]
        else:
            entryName = path

        self.callBackGetter(entryName, indices)

        if isinstance(path, str):
            path = self._resolveEntryPath(path)

        if not isinstance(indices, list):
            if isinstance(indices, tuple):
                indices = list(indices)
            else:
                indices = [indices]



        data = self.dataStructure.getDataEntry(self, path, indices, hStack)
        return data

    def setDataEntry(self, entryName, indices, data, restrictRange=False):
        '''
        Sets the data points for the required data entry (or alias).

        :param entryName: the path to the requested entry as an array.
                     e.g. ['steps', 'subSteps', 'subActions']
                     path may also be a string which is equivalent to an array
                     containing only one element
        :param indices: the hierarchical indices (depending on the hierarchy, it
                        can have different number of elements) as an array.
                        If the number of indices is less than the depth of the
                        hierarchy (less than the length of the path), all other
                        indices will be treated as "...".
                        indices may also be a number which is equivalent to an
                        array containing only one element
                        WARNING: The indices are starting at '0'. Hence, the
                        second episode has the index '1'.
        :param data: The data to set.
        :param restrictRange: If set to True, the minRange/maxRange parameters
                              are checked (optional, defaults to True)
        '''
        if data is None:
            raise ValueError('The data attribute is None.')

        numDimensions = self.dataManager.getNumDimensions(entryName)

        if isinstance(entryName, str):
            entryName = self._resolveEntryPath(entryName)

        if not isinstance(indices, list):
            if isinstance(indices, tuple):
                indices = list(indices)
            else:
                indices = [indices]

        if (isinstance(data, np.ndarray) and len(data.shape) == 1):
            if numDimensions > 1:
                data = np.expand_dims(data, axis=0)
            else:
                data = np.expand_dims(data, axis=1)

        return self.dataStructure.setDataEntry(self, entryName, indices, data)

    def getDataEntryList(self, entryPaths, indices):
        '''
        Similar to getDataEntry, but returns a list of results for each entry.
        '''
        dataEntryList = []
        for entry in entryPaths:
            if isinstance(entry, tuple):
                stackedEntry = None
                for subEntry in entry:
                    if stackedEntry is None:
                        stackedEntry = self.getDataEntry(subEntry, indices)
                    else:
                        stackedEntry = np.hstack((stackedEntry,
                                                 self.getDataEntry(subEntry,
                                                                   indices)))
                dataEntryList.append(stackedEntry)
            else:
                dataEntryList.append(self.getDataEntry(entry, indices))
        return dataEntryList



    def setDataEntryList(self, entryPaths, indices, dataEntryList):
        '''
        Similar to setDataEntry, but works for lists of entries.
        '''
        for i in range(0, len(entryPaths)):
            entry = entryPaths[i]
            if isinstance(entry, tuple):
                index = 0
                for j in range(0, len(entry)):
                    subEntry = entry[j]
                    subEntryName = subEntry
                    if isinstance(subEntryName, list):
                        subEntryName = subEntry[-1]
                    numDimensions = self.entryInfoMap[subEntryName].numDimensions

                    if len(numDimensions) > 1:
                        raise ValueError('Data matrices can not be stacked')
                    else:
                        numDimensions = numDimensions[0]
                    dataMatrix = dataEntryList[i]

                    if len(dataMatrix.shape) == 1:
                        dataMatrix = dataMatrix[index:(index + numDimensions)]
                    else:
                        dataMatrix = dataMatrix[:, index:(index + numDimensions)]
                    self.setDataEntry(subEntry, indices, dataMatrix)
                    index += numDimensions
                pass
            else:
                self.setDataEntry(entry, indices, dataEntryList[i])

    def resetFeatureTags(self):
        '''
        Resets the feature tags of all features in the data object.
        This NEEDS to be done whenever we write new data into the
        data structure, for example, when we sample new episodes.
        Otherwise the feature generators would not realize that the
        features need to be recomputed
        '''
        for dataEntry in self.entryInfoMap:
            if self.entryInfoMap[dataEntry].isFeature:
                numElements = self.getNumElements(dataEntry)

                self.setDataEntry(dataEntry + '_validFlag', ...,
                                  np.zeros((numElements,1),dtype=bool))

    def reserveStorage(self, numElements, indices = None):
        '''Allocates memory for `numElements` elements

        :param numElements: The number of elements that the data structure
                            should be able to handle.
        :change No "varargin" needed anymore
        '''

        subDataStructures = self.dataStructure.getSubdataStructures(indices)
        for subData in subDataStructures:
            subData.reserveStorage(numElements)

    def mergeData(self, other, inFront=False):
        '''
        Merges two data objects. The data from the second data object
        is either added in the back or in the front of the data points
        of the current object.
        :param other: The other data object
        :param inBack: If True, adds the data to the back
        '''
        otherStructure = other.dataStructure

        self.dataStructure.mergeDataStructures(other.dataStructure, inFront=inFront)

    def printDataAliases(self):

        for key, value in self.entryInfoMap.items():

            print(key, ': NumDimensions: ', value.numDimensions, ', Depth: ', value.depth, ', entryList: ', value.entryList);


class DataWriter(object):

    def __init__(self):

        self.writeEntries = []
        self.result = None
        self.isFlatIndex = False

    def addWriteEntry(self, writeEntry, indices, writeValues):

        self.writeEntries.append((writeEntry, indices, writeValues))

    def addWriteEntries(self, writeEntries, indices, writeValues):

        for (entry, value) in zip(writeEntries,writeValues):
            self.writeEntries.append((entry, indices, value))

    def reset(self):
        self.writeEntries.clear()

    def apply(self, data):
        if self.isFlatIndex:
            for (entry, index, value) in self.writeEntries:
                data.setDataEntryFlat(entry, index, value)
        else:
            for (entry, index, value) in self.writeEntries:
                data.setDataEntry(entry, index, value)

        result = self.result
        self.result = None
        self.reset()
        return result

    def setResult(self, result):
        self.result = result


class DataView(Data):
    def __init__(self, data, index):
        for key in ('entryInfoMap', 'states', 'dataManager', 'empty', 'tensorDictionary', 'dataStructure'):
            self.__dict__[key] = data.__dict__[key]

        self.isFlatIndex = False
        if isinstance(index, Data.FlatIndex):
            self.activeIndex = index.flatIndex
            self.isFlatIndex = True
        elif isinstance(index, list):
            self.activeIndex = index.copy()
        else:
            self.activeIndex = index

        if not isinstance(self.activeIndex, tuple):
            self.activeIndex = (self.activeIndex,)
