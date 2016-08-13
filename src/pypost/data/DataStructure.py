import numpy as np

from pypost.data.DataAlias import DataAlias
from scipy.sparse import csr_matrix
from pypost.common.SettingsClient import SettingsClient
from inspect import isfunction


class DataStructure(SettingsClient):
    '''
    DataStructure handles the data structure (containing real data) for the
    data object.
    '''

    def __init__(self, dataManager, numElements, isTimeSeries = False):

        '''Constructor'''
        SettingsClient.__init__(self)

        self.dataStructureLocalLayer = dict()
        self.dataEntries = dict()
        self.numElements = numElements
        self.nextLayer = None
        self.isTimeSeries = isTimeSeries
        self.dataManager = dataManager

    def getNumElementsForIndex(self, depth, indices=[]):
        if not isinstance(indices, list):
            indices = [indices]
        while len(indices) <= depth:
            indices.append(...)


        if (depth > 0):
            if (not self.nextLayer):
                raise ValueError('Hierarchical Index: Could not find hierarchy! {0}',format(indices))
            numElements = 0
            if indices[0] == Ellipsis:
                nextLayerStructures = self.nextLayer
            elif isinstance(indices[0], (int, slice)):
                nextLayerStructures = self.nextLayer[indices[0]]
            else:
                nextLayerStructures = [self.nextLayer[i] for i in indices[0]]
            indices = indices[1:]
            for i in range(0,len(nextLayerStructures)):
                numElements += nextLayerStructures[i].getNumElementsForIndex(depth - 1, indices)
            return numElements
        else:
            if indices[0] == Ellipsis:
                return self.numElements
            elif (self.nextLayer):
                return len(self.nextLayer[indices[0]])
            else:
                standardEntry = next(iter(self.dataEntries))
                return self.dataStructureLocalLayer[standardEntry][indices[0]].shape[0]


    def createEntry(self, name, dataEntry):
        '''Stores a new data entry in the local layer of the data structure

        :param name: The name of the entry
        :type name: string
        :param entry: The entry that will be added to the local layer
        :type entry: DataAlias or numpy.ndarray or DataStructure
        '''
        if name in self.dataStructureLocalLayer:
            raise ValueError("Cannot redefine entry")
        if (self.isTimeSeries):
            numElements = self.numElements + 1
        else:
            numElements = self.numElements

        if (not dataEntry.takeFromSettings):
            self.dataStructureLocalLayer[name] = dataEntry.createDataMatrix(numElements)
        else:
            def getEntryFromSettings(data, indices):
                if indices is Ellipsis:
                    numElementsFunc = numElements
                if isinstance(indices, int):
                    numElementsFunc = 1
                elif isinstance(indices, list):
                    numElementsFunc = len(indices)
                elif isinstance(indices, slice):
                    numElementsFunc = indices.stop - indices.start
                singleEntry = self.settings.getProperty(dataEntry.name)
                entry = np.tile(singleEntry, (numElementsFunc, 1))
                return entry

            self.dataStructureLocalLayer[name] = getEntryFromSettings

        self.dataEntries[name] = dataEntry

    def createAlias(self, name, aliasObj):
        if name in self.dataStructureLocalLayer:
            raise ValueError("Cannot redefine entry")
        self.dataStructureLocalLayer[name] = aliasObj

    def createAliasSubDataStructure(self, name, aliasObj):
        self.nextLayer = aliasObj
        self.createAlias(name, aliasObj)

    def __len__(self):
        return len(self.dataStructureLocalLayer)

    def __contains__(self, name):
        return name in self.dataStructureLocalLayer

    def __setitem__(self, name, item):
        # item contains 'real' data
        if isinstance(name, tuple):
            index = name[1]
            name = name[0]
        else:
            index = Ellipsis

        if name not in self.dataStructureLocalLayer:
            raise KeyError("The specified entry name is undefined")
        elif isfunction(self.dataStructureLocalLayer[name]):
            raise ValueError("Function Valued Data Entries can not be set. Optional Data Entry that is not activated?")
        elif isinstance(self.dataStructureLocalLayer[name], DataAlias):
            # asssigning to a data alias
            dataAlias = self.dataStructureLocalLayer[name]
            index = dataAlias.modifyIndex(index, self.numElements)
            currentIndexInItem = 0

            for entryName, slice_ in dataAlias.entryList:
                # calculate the dimensions (width) of the current entry
                l = self[entryName][:, slice_].shape[1]
                entry = self.dataStructureLocalLayer[entryName]

                if isinstance(entry, DataAlias):
                    # dataAlias contains another DataAlias (entry)
                    # we have to update it manually (explicit read and
                    # write)

                    self[(entryName, index)] = item[:, currentIndexInItem:currentIndexInItem + l]
                else:
                    if (index == Ellipsis):
                        index = slice(0, self.numElements)

                    # the entry is an ndarray
                    # writing directly to the ndarray...
                    entry[index, slice_] = \
                                    item[:, currentIndexInItem:currentIndexInItem + l]

                    currentIndexInItem += l

        else:
            dataEntry = self.dataEntries[name]
            dataEntry.isCorrectDataType(item)

            if (index == Ellipsis):
                index = slice(0,self.numElements)

            if isinstance(item, (np.ndarray, csr_matrix)):
                dataFromStruct = self.dataStructureLocalLayer[name][index,:]
                dataShape = dataFromStruct.shape
                newDataShape = item.shape

                if (len(newDataShape) > 1 and newDataShape[0] == 1):
                    newDataShape = (newDataShape[1],)
                if (len(dataShape) > 1 and dataShape[0] == 1):
                    dataShape = (dataShape[1],)
                # assigning to a 'real' data entry (a matrix)
                if dataShape != newDataShape:
                    raise ValueError("The shape of the specified matrix (%s) for data entry %s "
                                     " doesn't match the existing entry (%s)"
                                     % (newDataShape, name, dataShape))

            self.dataStructureLocalLayer[name][index, :] = item


    def __getitem__(self, name):

        if isinstance(name, tuple):
            index = name[1]
            name = name[0]
        else:
            index = Ellipsis

        if name not in self.dataStructureLocalLayer:
            raise ValueError("The element '" + str(name) + "' does not exist.")

        if isfunction(self.dataStructureLocalLayer[name]):
            return self.dataStructureLocalLayer[name](self, index)
        elif isinstance(self.dataStructureLocalLayer[name], DataAlias):

            # get the data from a DataAlias
            data = None
            dataAlias = self.dataStructureLocalLayer[name]
            index = dataAlias.modifyIndex(index, self.numElements)
            for entryName, slice_ in dataAlias.entryList:
                entry = self.dataStructureLocalLayer[entryName]
                if isinstance(entry, DataAlias):
                    # dataAlias contains another DataAlias (entry)
                    entry = self[(entryName, index)]
                elif isinstance(entry, np.ndarray):
                    if (index == Ellipsis):
                        index = slice(0, self.numElements)
                    entry = entry[index]
                else:
                    raise ValueError("Unknown type of the data alias entry")

                if data is None:
                    data = entry[:, slice_]
                else:
                    entryData = entry[:, slice_]
                    data = np.hstack((data, entryData))

            return data
        elif isinstance(self.dataStructureLocalLayer[name], list):
            # get the data from a subDataStructure
            return self.dataStructureLocalLayer[name]
        else:
            if (index == Ellipsis):
                index = slice(0,self.numElements)

            return self.dataStructureLocalLayer[name][index]



    def getDataEntry(self, path, indices):
        '''
        Returns the data points from the required data entry (or
        alias).

        :param path: the path to the requested entry as an array.
                     e.g. ['steps', 'subSteps', 'subActions']
        :param indices: the hierarchical indices (depending on the hierarchy, it
                        can have different number of elements) as an array.
                        If the number of indices is less than the depth of the
                        hierarchy (less than the length of the path), all other
                        indices will be treated as "...".
                        indices may also be a number which is equivalent to an
                        array containing only one element
        '''

        while len(indices) < len(path):
            indices.append(...)

        if len(indices) > len(path):
            indices = indices[0:len(path)]

        if len(path) == 0:
            raise ValueError("Empty paths are not allowed")
        elif len(path) == 1:
            # get the data from the current layer
            if indices[0] == Ellipsis:
                return self[path[0]]
            elif isinstance(indices[0], (slice, list)):
                return self[path[0]][indices]
            elif isinstance(indices[0], int):
                if (indices[0] >= self[path[0]].shape[0]):
                    raise ValueError("Invalid data type: indices[0]: ", indices[0])
                return np.array(
                    [self[path[0]][indices[0]]])
            else:
                raise ValueError("Invalid data type: indices[0]: ", indices[0])
        else:
            # get the data from lower layers
            data = None
            subLayers = None

            if indices[0] == Ellipsis:
                subLayers = self.dataStructureLocalLayer[path[0]]
            elif isinstance(indices[0], slice):
                subLayers = self.dataStructureLocalLayer[path[0]][indices[0]]
            elif isinstance(indices[0], int):
                subLayers = [self.dataStructureLocalLayer[path[0]][indices[0]]]
            elif isinstance(indices[0], list):
                subLayers = [self.dataStructureLocalLayer[path[0]][i] for i in indices[0]]
            else:
                raise ValueError("Invalid data type: indices[0]: ", indices[0])

            for subDataStructure in subLayers:
                # get the data from the data structure of a lower layer
                subData = subDataStructure.getDataEntry(path[1:], indices[1:])

                if data is None:
                    data = subData
                else:
                    data = np.vstack((data, subData))

            return data

    def setDataEntry(self, path, indices, data):
        '''
        Sets the data points for the required data entry (or
        alias).

        :param path: the path to the requested entry as an array.
                     e.g. ['steps', 'subSteps', 'subActions']
        :param indices: the hierarchical indices (depending on the hierarchy, it
                        can have different number of elements) as an array.
                        If the number of indices is less than the depth of the
                        hierarchy (less than the length of the path), all other
                        indices will be treated as "...".
                        indices may also be a number which is equivalent to an
                        array containing only one element
        :param data: the data to be set
        '''

        while len(indices) < len(path):
            indices.append(...)

        if len(path) == 0:
            raise ValueError("Empty paths are not allowed")
        elif len(path) == 1:
            # set the data in the current layer
            if indices[0] == Ellipsis:
                # set the data for all iterations of the requested entry
                self[path[0]] = data
            elif isinstance(indices[0], (slice, list, int)):


                # set the data for the selected iterations of the requested
                # entry
                dataShape = self[(path[0],indices[0])].shape
                newDataShape = data.shape

                if (len(newDataShape) > 1 and newDataShape[0] == 1):
                    newDataShape = (newDataShape[1],)
                if (len(dataShape) > 1 and dataShape[0] == 1):
                    dataShape = (dataShape[1],)

                if newDataShape != dataShape:
                    raise ValueError("The shape of the specified matrix (%s)"
                                     " doesn't match the expected shape (%s)"
                                     % (newDataShape, dataShape))

                #temp = self[path[0]]
                #temp[indices[0]] = data
                self[(path[0],indices[0])] = data
#            elif isinstance(indices[0], int):
#                # set the data for a single iteration of the requested entry
#
#               if len(data.shape) == 2:
                    # we only want to store a single vector, not an array
                    # containing only this vector (we want [1, 1] instead of
                    # [[1,1]])
#
#                    if data.shape[0] != 1:
#                        raise ValueError('The given data object is a ' +
#                                         'matrix, not a vector.')
#
#                    data = data[0]
#
#                self[path[0]][indices[0]] = data
            else:
                raise ValueError("Invalid data type: indices[0]")

        else:
            # set the data in lower layers
            subLayers = None

            if indices[0] == Ellipsis:
                # devide the data into len(subLayers) parts and pass each of
                # these subData's to the corresponding subLayer
                subLayers = self.dataStructureLocalLayer[path[0]]
                subDataLen = int(data.shape[0] / len(subLayers))

                subDataShape = subLayers[0].getDataEntry(path[1:],
                                                         indices[1:]).shape

                if (data.shape[0] != subDataShape[0] * len(subLayers) or
                    data.shape[1] != subDataShape[1]):
                    raise ValueError("The shape of the specified matrix (%s)"
                                     " doesn't match the expected shape (%s)"
                                     % (data.shape,
                                        (subDataShape[0] * len(subLayers),
                                         subDataShape[1])))

                i = 0
                for subLayer in subLayers:
                    subData = data[i * subDataLen:(i + 1) * subDataLen]
                    subLayer.setDataEntry(path[1:], indices[1:], subData)
                    i += 1

            elif isinstance(indices[0], (slice, list)):
                # devide the data into several parts (depending on the given
                # slice) and pass each of these to the corresponding subLayer.
                if isinstance(indices[0], slice):
                    subLayers = self.dataStructureLocalLayer[path[0]][indices[0]]
                else:
                    subLayers = [self.dataStructureLocalLayer[path[0]][i] for i in indices[0]]
                subDataLen = int(data.shape[0] / len(subLayers))

                subDataShape = subLayers[0].getDataEntry(path[1:],
                                                         indices[1:]).shape

                if (data.shape[0] != subDataShape[0] * len(subLayers) or
                    data.shape[1] != subDataShape[1]):
                    raise ValueError("The shape of the specified matrix (%s)"
                                     " doesn't match the expected shape (%s)"
                                     % (data.shape,
                                        (subDataShape[0] * len(subLayers),
                                         subDataShape[1])))

                i = 0
                for subLayer in subLayers:
                    subData = data[i:i + subDataLen]
                    subLayer.setDataEntry(path[1:], indices[1:], subData)
                    i += subDataLen
            else:
                # pass the data to excaltly one lower layer
                subLayer = self.dataStructureLocalLayer[path[0]][indices[0]]
                subLayer.setDataEntry(path[1:], indices[1:], data)

    def getSubdataStructures(self, indices = None):

        if indices is None or not indices:
            return [self]

        if not isinstance(indices, list):
            indices = [indices]

        if (indices[0] == Ellipsis):
            indices[0] = slice(0, self.numElements)
        elif isinstance(indices[0], int):
            indices[0] = slice(indices[0], indices[0] + 1)

        if (not self.nextLayer):
            raise ValueError('Can not find given hierarchical index')

        if len(indices) == 1:
            if (isinstance(indices[0], (slice, int))):
                return self.nextLayer[indices[0]]
            else:
                return [self.nextLayer[i] for i in indices[0]]
        else:

            if (isinstance(indices[0], (slice, int))):
                subData = self.nextLayer[indices[0]]
            else:
                subData = [self.nextLayer[i] for i in indices[0]]

            if isinstance(subData, list):
                newSubdataForLayer = []
                for i in range(0,len(subData)):
                    newSubdataForLayer = newSubdataForLayer + subData[i].getSubdataStructures(indices[1:])
                return newSubdataForLayer
            else:
                return subData.getSubdataStructures(indices[1:])



    def reserveStorage(self, numElements):
        '''
        Reserves more storage for a data structure. numElements can be a vector
        that also contains the number of data points to add to the lower levels
        of the hierarchy. This function should only be called by the data
        object.

        :param data.DataStructure dataStructure: The DataStructure to be
                                                 modified
        :param numElements: A vector containing the number of elements to add
                            for each layer
        :type numElemenst: list of ints
        '''


        # no indicing... we need to reserve storage for current layer
        if isinstance(numElements, list):
            numElementsLocal = numElements[0]
            numElements = numElements[1:]
        else:
            numElementsLocal = numElements
            numElements = []

        numElementsEntry = numElementsLocal
        if (self.isTimeSeries):
            numElementsEntry += 1

        self.numElements = numElementsLocal
        for name, entry in self.dataEntries.items():
            currentSize = self.dataStructureLocalLayer[name].shape[0]
            if currentSize < numElementsEntry:
                self.dataStructureLocalLayer[name] = np.vstack(
                    (self.dataStructureLocalLayer[name],
                     np.zeros((numElementsEntry - currentSize,
                               entry.numDimensions[0]))))
            else:
                self.dataStructureLocalLayer[name] = np.delete(
                    self.dataStructureLocalLayer[name],
                    slice(numElementsEntry, None, None), 0)

        if self.nextLayer is not None and numElements:

            subStructureList = self.nextLayer
            currentSize = len(subStructureList)
            diff = numElementsLocal - currentSize
            # adapt amount of sub structures
            if (diff > 0):
                for i in range(0, diff):
                    subStructureList.append(self.dataManager.subDataManager._createDataStructure(numElements[0]))
            else:
                for i in range(0, -diff):
                    subStructureList.pop(-1)
            for subStructure in subStructureList:
                subStructure.reserveStorage(numElements)