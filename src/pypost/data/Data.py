import numpy as np
import copy

from pypost.data.DataStructure import DataStructure
from pypost.data.DataEntry import DataType


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

        self.activeIndex = Ellipsis
        # create the entryInfoMap

        aliasNames = self.dataManager.getAliasNames()
        entryNames = self.dataManager.getEntryNames()
        for name in aliasNames:
            depth = self.dataManager.getDataEntryDepth(name)
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
        self.activeIndex = index
        if isinstance(self.activeIndex, tuple):
            self.activeIndex = list(self.activeIndex)
        return self

    def __setattr__(self, name, value):
        indexPreprocessor = name.find('_')
        if indexPreprocessor > 0:
            nameEntry = name[:indexPreprocessor]
        else:
            nameEntry = name
        if (value is not None and name != 'entryInfoMap' and nameEntry in self.entryInfoMap):
            return self.setDataEntry(name, self.activeIndex, value)
        else:
            return super().__setattr__(name, value)

    def __getattribute__(self, name):
        indexPreprocessor = name.find('_')
        if indexPreprocessor > 0:
            nameEntry = name[:indexPreprocessor]
        else:
            nameEntry = name

        if (name != 'entryInfoMap' and nameEntry in self.entryInfoMap):
            return self.getDataEntry(name, self.activeIndex)
        else:
            return super().__getattribute__(name)

    def __rshift__(self, function):
        '''Operator for applying data manipulation functions'''

        if hasattr(function, '__call__') and hasattr(function, 'dataFunctionDecorator'):
            function.dataFunctionDecorator.dataFunction(function, self, self.activeIndex, registerOutput = True)
            return self
        else:
            raise ValueError('Operator >> can only be applied to manipulation functions or tuples of manipulation functions'
                             'and index')

    def __ge__(self, function):
        '''Operator for applying data manipulation functions'''

        if hasattr(function, '__call__') and hasattr(function, 'dataFunctionDecorator'):
            return function.dataFunctionDecorator.dataFunction(function, self, self.activeIndex, registerOutput = True)

        else:
            raise ValueError('Operator >> can only be applied to manipulation functions or tuples of manipulation functions'
                             'and index')

    def __gt__(self, function):
        '''Operator for applying data manipulation functions'''

        if hasattr(function, '__call__') and hasattr(function, 'dataFunctionDecorator'):
            return function.dataFunctionDecorator.dataFunction(function, self, self.activeIndex, registerOutput=False)

        else:
            raise ValueError(
                'Operator >> can only be applied to manipulation functions or tuples of manipulation functions'
                'and index')

    def completeLayerIndex(self, depth, indices):
        '''This function completes the hierarchical indicing for the internal
        functions for accessing the data. E.g., if not enough indices are
        specified, it appends appropriate slices.

        :param depth: The depth of the indices path
        :param indices: The (potentially incomplete) indices
        :returns: The complete indices array
        '''
        if not isinstance(indices, list):
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
                dataStructure = dataStructure[manager.name][0]
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
            indices = [indices]
        while len(indices) <= depth:
            indices.append(...)

        return self.dataStructure.getNumElementsForIndex(depth, indices)

    def _resolveEntryPath(self, name):
        path = []

        index = name.find('_')
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

        index = path.find('_')
        if index < 0:
            return (path, '')
        else:
            return (path[:index], path[index + 1:])


    def getDataEntry(self, path, indices=[], cloneData=True):
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

        if entryName in self.entryInfoMap:
            dataEntryInfo = self.entryInfoMap[entryName]
            if (dataEntryInfo.callBackGetter):
                callBack = dataEntryInfo.callBackGetter
                dataEntryInfo.callBackGetter = None
                self[indices] >> callBack
                dataEntryInfo.callBackGetter = callBack

        if isinstance(path, str):
            path = self._resolveEntryPath(path)

        if not isinstance(indices, list):
            indices = [indices]


        data = self.dataStructure.getDataEntry(self, path, indices)
        return data

    def setDataEntry(self, path, indices, data, restrictRange=False):
        '''
        Sets the data points for the required data entry (or alias).

        :param path: the path to the requested entry as an array.
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

        if isinstance(path, str):
            path = self._resolveEntryPath(path)

        if not isinstance(indices, list):
            indices = [indices]


        return self.dataStructure.setDataEntry(self, path, indices, data)

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

    #def resetFeatureTags(self):
    #    '''
    #    Resets the feature tags of all features in the data object.
    #    This NEEDS to be done whenever we write new data into the
    #    data structure, for example, when we sample new episodes.
    #    Otherwise the feature generators would not realize that the
    #    features need to be recomputed
    #    '''
    #    for dataEntry in self.entryInfoMap:
    #        if self.entryInfoMap[dataEntry].isFeature:
    #            numElements = self.getNumElements(dataEntry)
    #
    #            self.setDataEntry(dataEntry.name, ...,
    #                              np.zeros(numElements, 1))

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
