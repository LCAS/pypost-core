'''
Created on 12.11.2015

@author: sebastian


Notes: matlab.getDataEntry('actions', :, 1, -1)
       statt ':' könnte man 0 verwenden
'''

import numpy as np
from IPython.external.path._path import path


class DataEntryInfo(object):
    '''
    Stores meta data about entries and aliases.
    '''

    def __init__(self, depth, entryList, numDimensions,
                 minRange, maxRange):
        self.depth = depth
        self.entryList = entryList
        self.numDimensions = numDimensions
        self.minRange = minRange
        self.maxRange = maxRange


class Data(object):
    '''
    classdocs
    '''

    def __init__(self, dataManager, dataStructure):
        '''
        Constructor
        '''
        self.dataManager = dataManager
        self.dataStructure = dataStructure
        self.entryInfoMap = {}

        self.init()

    def init(self):
        '''
        Stores meta data for each data entry to make access simple and fast.
        '''
        aliasNames = self.dataManager.getAliasNames()
        for name in aliasNames:
            depth = self.dataManager.getDataEntryDepth(name)
            alias = self.dataManager.getDataAlias(name)
            self.entryInfoMap[name] = \
                DataEntryInfo(depth, alias.entryList, alias.numDimensions,
                              self.dataManager.getMinRange(name),
                              self.dataManager.getMaxRange(name))

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

    def _resolveEntryPath(self, name):
        path = []
        if name in self.entryInfoMap:
            depth = self.entryInfoMap[name].depth
            dataManager = self.dataManager.subDataManager
            while dataManager is not None and depth > 0:
                path.append(dataManager.name)
                dataManager = dataManager.subDataManager
                depth -= 1
        path.append(name)
        # print("%s -> %s" % (name, path))
        return path

    def getNumElementsForIndex(self, depth, indices=[]):
        while len(indices) <= depth:
            indices.append(...)

        numElements = 1
        dm = self.dataManager
        subStructure = self.dataStructure
        while depth > 0:
            dm = dm.subDataManager
            subStructureList = subStructure[dm.name]
            if indices[0] is not Ellipsis:
                subStructureList = subStructureList[indices[0]]
            numElements *= len(subStructureList)
            subStructure = subStructureList[0]
            indices = indices[1:]
            depth -= 1

        for name, entry in subStructure.dataStructureLocalLayer.items():
            if isinstance(entry, np.ndarray):
                numElements *= subStructure[name][indices[0]].shape[0]
                break

        return numElements

    def getDataEntry(self, path, indices=[]):
        '''
        Returns the data points from the required data entry (or alias).
        @param path the path to the requested entry as an array
                    e.g. ['steps', 'subSteps', 'subActions'] or
                    simply the name of the entry.
        @param indices the hierarchical indices (depending on the hierarchy, it
                       can have different number of elements) as an array.
                       If this parameter is omitted or the number of indices is
                       less than the depth of the hierarchy (less than the
                       length of the path), all other indices will be treated
                       as "...".
                       indices may also be a number which is equivalent to an
                       array containing only one element
        '''
        if isinstance(path, str):
            path = self._resolveEntryPath(path)

        if isinstance(indices, int) or indices == Ellipsis:
            indices = [indices]

        return self.dataStructure.getDataEntry(path, indices)

    def setDataEntry(self, path, indices, data):
        '''
        Sets the data points for the required data entry (or alias).
        @param path the path to the requested entry as an array.
                    e.g. ['steps', 'subSteps', 'subActions']
                    path may also be a string which is equivalent to an array
                    containing only one element
        @param indices the hierarchical indices (depending on the hierarchy, it
                       can have different number of elements) as an array.
                       If the number of indices is less than the depth of the
                       hierarchy (less than the length of the path), all other
                       indices will be treated as "...".
                       indices may also be a number which is equivalent to an
                       array containing only one element
                       WARNING: The indices are starting at '0'. Hence, the
                       second episode has the index '1'.
        '''
        if isinstance(path, str):
            path = self._resolveEntryPath(path)

        if isinstance(indices, int) or indices == Ellipsis:
            indices = [indices]

        return self.dataStructure.setDataEntry(path, indices, data)

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

    def reserveStorage(self, numElements):
        self.dataManager.reserveStorage(self.dataStructure, numElements)
