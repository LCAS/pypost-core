import numpy as np

from pypost.data.DataAlias import DataAlias
from pypost.data.DataEntry import DataEntry
from scipy.sparse import csr_matrix
from pypost.common.SettingsClient import SettingsClient
import copy

class DataStructure(SettingsClient):
    '''
    DataStructure handles the data structure (containing real data) for the
    data object.
    '''

    def __init__(self, dataManager, numElements, isTimeSeries = False):

        '''Constructor'''
        SettingsClient.__init__(self)

        self.name = dataManager.name
        self.dataStructureLocalLayer = dict()
        self.dataEntries = dict()
        self.numElements = numElements
        self.nextLayer = None
        self.isTimeSeries = isTimeSeries
        self.dataManager = dataManager

        self.currentData = None

    def getNumElementsForIndex(self, depth, indices=[]):
        if not isinstance(indices, list):
            indices = [indices]
        while len(indices) <= depth:
            indices.append(...)


        if (depth > 0):
            if (not self.nextLayer):
                raise ValueError('Hierarchical Index: Could not find hierarchy! {0}',format(indices))
            numElements = 0
            nextLayer = self.dataStructureLocalLayer[self.nextLayer]
            if indices[0] == Ellipsis:
                nextLayerStructures = nextLayer
            elif isinstance(indices[0], slice):
                nextLayerStructures = nextLayer[indices[0]]
            elif isinstance(indices[0], int):
                nextLayerStructures = [nextLayer[indices[0]]]
            else:
                nextLayerStructures = [nextLayer[i] for i in indices[0]]
            indices = indices[1:]
            for i in range(0,len(nextLayerStructures)):
                numElements += nextLayerStructures[i].getNumElementsForIndex(depth - 1, indices)
            return numElements
        else:
            if indices[0] == Ellipsis:
                return self.numElements

            elif isinstance(indices[0], list):
                return len(indices[0])
            # Todo Check this:
            elif isinstance(indices[0], slice):
                step_size = 1 if indices[0].step is None else indices[0].step
                return (indices[0].stop - indices[0].start) // step_size
            else:
                return 1
            # This is problematic since self.dataEntries (a dict) is unordered and hence standardEntry (and its shape)
            # are 'non deterministically' chosen and do not always (but sometimes) match the desired value...
            # standardEntry = next(iter(self.dataEntries))
            # return self.dataStructureLocalLayer[standardEntry].data[indices[0]].shape[0]


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

        newDataEntry = copy.copy(dataEntry)

        if (not newDataEntry.takeFromSettings):
            newDataEntry.createDataMatrix(numElements)

        self.dataStructureLocalLayer[name] = newDataEntry

        self.dataEntries[name] = newDataEntry

    def createAlias(self, name, aliasObj):
        if name in self.dataStructureLocalLayer:
            raise ValueError("Cannot redefine entry")
        self.dataStructureLocalLayer[name] = aliasObj

    def createAliasSubDataStructure(self, name, aliasObj):
        self.nextLayer = name
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

        indexPreprocessor = name.find('__')
        dataPreprocessor = None
        if indexPreprocessor > 0:
            dataPreprocessor = self.dataManager.getDataPreprocessorInverse(name[indexPreprocessor + 2:])
#            item = dataPreprocessor(item.copy())
            name = name[:indexPreprocessor]

        dataItem = self.dataStructureLocalLayer[name]
        if name not in self.dataStructureLocalLayer:
            raise KeyError("The specified entry name is undefined")
        elif isinstance(dataItem, DataAlias):
            # asssigning to a data alias
            dataAlias = self.dataStructureLocalLayer[name]
            index = dataAlias.modifyIndex(index, self.numElements)
            currentIndexInItem = 0

            if (isinstance( item, (np.ndarray, csr_matrix))  and len(item.shape) == 1 and dataAlias.numDimensions[0] == item.shape[0]):
                item.resize((1, dataAlias.numDimensions[0]))

            for entryName, slice_ in dataAlias.entryList:
                # calculate the dimensions (width) of the current entry

                entry = self.dataStructureLocalLayer[entryName]

                if (dataAlias.useConcatVertical):
                    shape = self[entryName][index, slice_].shape
                    if (len(shape) == 1):
                        l = 1
                    else:
                        l = shape[0]

                    if isinstance(entry, DataAlias):
                        # dataAlias contains another DataAlias (entry)
                        # we have to update it manually (explicit read and
                        # write)

                        if isinstance(item, (csr_matrix, np.ndarray)):
                            # the entry is an ndarray
                            # writing directly to the ndarray...

                            self[(entryName, index)] = item[currentIndexInItem:currentIndexInItem + l, :]
                        else:
                            self[(entryName, index)] = item
                    else:
                        if (index == Ellipsis):
                            index = slice(0, self.numElements)

                        if isinstance(item, (csr_matrix, np.ndarray)):
                            # the entry is an ndarray
                            # writing directly to the ndarray...

                            entry.data[index, slice_] = item[currentIndexInItem:currentIndexInItem + l, :]
                        else:
                            entry.data[index, slice_] = item
                        currentIndexInItem += l
                else:
                    l = self[entryName][:, slice_].shape[1]
                    if isinstance(entry, DataAlias):
                        # dataAlias contains another DataAlias (entry)
                        # we have to update it manually (explicit read and
                        # write)

                        if isinstance(item, (csr_matrix, np.ndarray)):
                            # the entry is an ndarray
                            # writing directly to the ndarray...
                            self[(entryName, index)] = item[:, currentIndexInItem:currentIndexInItem + l]

                            currentIndexInItem += l
                        else:
                            # item is numerical (float, int, bool)
                            self[(entryName, index)] = item
                    else:
                        if (index == Ellipsis):
                            index = slice(0, self.numElements)

                        if isinstance(item, (csr_matrix, np.ndarray)):
                            # the entry is an ndarray
                            # writing directly to the ndarray...
                            entry.data[index, slice_] = item[:, currentIndexInItem:currentIndexInItem + l]

                            currentIndexInItem += l
                        else:
                            # item is numerical (float, int, bool)
                            entry.data[index, slice_] = item


        elif isinstance(dataItem, DataEntry):
            dataEntry = dataItem
            dataEntry.isCorrectDataType(item)

            if (dataEntry.takeFromSettings):
                raise ValueError('Can not set deactivated optional data entry! Did you forget to activate it?')
            else:
                if (index == Ellipsis):
                    index = slice(0,self.numElements)

                if dataPreprocessor:
                    item = dataPreprocessor(item, dataEntry, index)

                if isinstance(item, (np.ndarray, csr_matrix)):
                    dataFromStruct = self.dataStructureLocalLayer[name].data[index,:]
                    dataShape = dataFromStruct.shape
                    newDataShape = item.shape

                    if (len(newDataShape) > 1 and newDataShape[0] == 1):
                        newDataShape = (newDataShape[1],)
                    if (len(dataShape) > 1 and dataShape[0] == 1):
                        dataShape = (dataShape[1],)
                    # assigning to a 'real' data entry (a matrix)
                    if (len(newDataShape) == 1 and len(dataShape) > 1):
                        if (newDataShape[0] != dataShape[1] and dataShape[1] > 1):
                            raise ValueError("The shape of the specified vector (%s) for data entry %s "
                                         " doesn't match the existing entry (%s)"
                                         % (newDataShape[0], name, dataShape[1]))
                        elif (newDataShape[0] != dataShape[0] and dataShape[1] == 1):
                            raise ValueError("The shape of the specified vector (%s) for data entry %s "
                                         " doesn't match the existing entry (%s)"
                                         % (newDataShape[0], name, dataShape[0]))
                    elif dataShape != newDataShape:
                        raise ValueError("The shape of the specified matrix (%s) for data entry %s "
                                         " doesn't match the existing entry (%s)"
                                        % (newDataShape, name, dataShape))
                dataEntry.data[index, :] = item


    def __getitem__(self, name):

        if isinstance(name, tuple):
            index = name[1]
            name = name[0]
        else:
            index = Ellipsis


        # Check for preProcessors
        indexPreprocessor = name.find('__')

        dataPreprocessor = None
        if indexPreprocessor > 0:
            dataPreprocessor = self.dataManager.getDataPreprocessorForward(name[indexPreprocessor + 2:])
            name = name[:indexPreprocessor]

        if name not in self.dataStructureLocalLayer:
            raise ValueError("The element '" + str(name) + "' does not exist.")

        dataItem = self.dataStructureLocalLayer[name]

        if isinstance(dataItem, list):
            return dataItem
        else:
            if isinstance(dataItem, DataAlias):
                # get the data from a DataAlias
                dataAlias = dataItem
                index = dataAlias.modifyIndex(index, self.numElements)

            if isinstance(index, tuple):
                data = self.getDataFromEntryOrAlias(dataItem, index[0])

                for i in range(1, len(index)):
                    data = np.hstack([data, self.getDataFromEntryOrAlias(dataItem, index[i])])
            else:
                # needs to be DataEntry or DataAlias
                assert isinstance(dataItem, (DataEntry, DataAlias)), 'We should only have Entries or Aliases at this point!'
                data = self.getDataFromEntryOrAlias(dataItem, index)

            if (dataPreprocessor):
                data = dataPreprocessor(data, dataItem, index)
            return data

    def getDataFromEntryOrAlias(self, dataItem, index):
        if isinstance(dataItem, DataAlias):
            dataAlias = dataItem
            # get the data from a DataAlias
            data = None
            for entryName, slice_ in dataAlias.entryList:
                entry = self.dataStructureLocalLayer[entryName]
                if isinstance(entry, DataAlias):
                    # dataAlias contains another DataAlias (entry)
                    entryData = self[(entryName, index)]
                elif isinstance(entry, DataEntry):
                    if (index == Ellipsis):
                        index = slice(0, self.numElements)
                    entryData = entry.data[index, :]
                else:
                    raise ValueError("Unknown type of the data alias entry")
                if (entryData.shape[0] > 0):
                    if len(entryData.shape) == 1:
                        entryData.resize((1, entryData.shape[0]))
                    if data is None:
                        data = entryData[:, slice_].copy()
                    else:
                        entryData = entryData[:, slice_]

                        if not dataItem.useConcatVertical:
                            data = np.hstack((data, entryData))
                        else:
                            data = np.vstack((data, entryData))

        elif isinstance(dataItem, list):
            # get the data from a subDataStructure
            data = self.dataStructureLocalLayer[dataItem.name]
        else:
            # needs to be DataEntry
            if dataItem.takeFromSettings:
                data = dataItem.getEntryFromSettings(index, self.numElements)
            else:
                if (index == Ellipsis):
                    index = slice(0, self.numElements)
                elif (isinstance(index, int)):
                    index = [index]
                data = dataItem.data[index].copy()



        return data

    def getDataEntry(self, dataObject, path, indices, hStack = False):
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

        self.currentData = dataObject
        while len(indices) < len(path):
            indices.append(...)

        if len(indices) > len(path):
            indices = indices[0:len(path)]

        # if isinstance(indices[0], tuple):
        #     hStack = True
        #     if (indices[0][0] == Ellipsis):
        #         indices[0] = Ellipsis
        #     else:
        #         indices[0] = list(indices[0])

        if len(path) == 0:
            raise ValueError("Empty paths are not allowed")
        elif len(path) == 1:
            # get the data from the current layer
            if indices[0] == Ellipsis:
                return self[path[0]]
            elif isinstance(indices[0], (slice, list, int, tuple)):
                return self[(path[0],indices[0])]
#            elif isinstance(indices[0], int):
#                dataTemp = self[path[0]]
#                if (indices[0] >= dataTemp.shape[0]):
#                    raise ValueError("Invalid index: index ouy of bounds: {} >= {}".format(indices[0],self[path[0]].shape[0]))
#                return np.array(dataTemp[indices[0]])
            else:
                raise ValueError("Invalid data type: indices[0]: ", indices[0])
        else:
            # get the data from lower layers
            data = None
            subLayers = None

            indexPreprocessor = path[-1].find('__')
            if indexPreprocessor > 0 and path[-1][indexPreprocessor + 2:] == '_T':
                path[-1] = path[-1][:indexPreprocessor]
                hStack = True

            if indices[0] == Ellipsis:
                subLayers = self.dataStructureLocalLayer[path[0]]
            elif isinstance(indices[0], slice):
                subLayers = self.dataStructureLocalLayer[path[0]][indices[0]]
            elif isinstance(indices[0], int):
                subLayers = [self.dataStructureLocalLayer[path[0]][indices[0]]]
            elif isinstance(indices[0], list):
                subLayers = [self.dataStructureLocalLayer[path[0]][i] for i in indices[0]]
            else:
                raise ValueError("Invalid data type: indices[0]: %s" % str(indices[0]))

            for subDataStructure in subLayers:
                # get the data from the data structure of a lower layer
                numElements = subDataStructure.numElements


                if (isinstance(indices[1], list)):
                    indexLocalSingle = [index for index in indices[1] if index < numElements]
                    numElementsLocal = len(indexLocalSingle)
                    indexLocalSingle =[indexLocalSingle]
                    indexLocal = indexLocalSingle + indices[2:]
                elif isinstance(indices[1], int):
                    numElementsLocal = int(indices[1] < numElements)
                    indexLocal = indices[1:]
                else:
                    indexLocal = indices[1:]
                    if (isinstance(indices[1], slice)):
                        numElementsLocal = indices[1].stop - indices[1].start
                    else:
                        # has to be Ellipsis
                        numElementsLocal = numElements

                if (numElementsLocal > 0):
                    subData = subDataStructure.getDataEntry(data, path[1:], indexLocal, hStack)

                    if data is None:
                        data = subData
                    else:
                        if (hStack is None or not hStack):
                            data = np.vstack((data, subData))
                        else:
                            if subData.shape[0] < data.shape[0]:
                                subData = np.vstack((subData, np.zeros((data.shape[0] - subData.shape[0], subData.shape[1])) * np.nan))
                            elif subData.shape[0] > data.shape[0]:
                                data = np.vstack((data, np.zeros((subData.shape[0] - data.shape[0], data.shape[1])) * np.nan))

                            data = np.hstack((data, subData))

            return data

    def setDataEntry(self, dataObject, path, indices, data):
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
        self.currentData = dataObject


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

                dataShape = self[(path[0], indices[0])].shape

                if (isinstance(data, (bool, int, float))):
                    newDataShape = (1,)
                else:
                    newDataShape = data.shape

                if (len(newDataShape) > 1 and newDataShape[0] == 1):
                    newDataShape = (newDataShape[1],)
                if (len(dataShape) > 1 and dataShape[0] == 1):
                    dataShape = dataShape[1:]

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
            # depth of entry is 2 or more
            # set the data in lower layers
            subLayers = None

            if indices[0] == Ellipsis or isinstance(indices[0], (slice, list)):
                # devide the data into several parts (depending on the given
                # slice) and pass each of these to the corresponding subLayer.
                if isinstance(indices[0], slice):
                    subLayers = self.dataStructureLocalLayer[path[0]][indices[0]]
                elif isinstance(indices[0], list):
                    subLayers = [self.dataStructureLocalLayer[path[0]][i] for i in indices[0]]
                else:
                    # index is Ellipsis... take all sublayers
                    subLayers = self.dataStructureLocalLayer[path[0]]

                numElementsList = [layer.getNumElementsForIndex(len(path) - 2, indices[1:]) for layer in subLayers]
                numElemetsSum = np.sum(numElementsList)

                if isinstance(data, np.ndarray) and len(data.shape) > 1:
                    if data.shape[0] != numElemetsSum:
                        raise ValueError("Number of rows of the specified matrix (%s)"
                                     " doesn't match the expected number of rows (%s)"
                                     % (data.shape[0], numElemetsSum))
                    indexStart = 0

                    i = 0
                    for subLayer in subLayers:
                        subData = data[indexStart:indexStart + numElementsList[i]]
                        subLayer.setDataEntry(dataObject, path[1:], indices[1:], subData)
                        indexStart += numElementsList[i]
                        i += 1
                else:
                    # we are having a numeric type or a vector... all elements should be set to this value
                    for subLayer in subLayers:
                        subLayer.setDataEntry(dataObject, path[1:], indices[1:], data)

            else:
                # pass the data to exactly one lower layer
                # index is only an int
                subLayer = self.dataStructureLocalLayer[path[0]][indices[0]]
                subLayer.setDataEntry(dataObject, path[1:], indices[1:], data)



    def getSubdataStructures(self, indices = None):

        if indices is None:
            return [self]

        if not isinstance(indices, list):
            indices = [indices]

        if len(indices) == 0:
            return [self]

        if indices[0] == Ellipsis:
            indices[0] = slice(0, self.numElements)
        elif isinstance(indices[0], int):
            indices[0] = slice(indices[0], indices[0] + 1)

        if not self.nextLayer:
            raise ValueError('Can not find given hierarchical index')

        nextLayer = self.dataStructureLocalLayer[self.nextLayer]
        if len(indices) == 1:
            if isinstance(indices[0], (slice, int)):
                return nextLayer[indices[0]]
            else:
                return [nextLayer[i] for i in indices[0]]
        else:

            if isinstance(indices[0], (slice, int)):
                subData = nextLayer[indices[0]]
            else:
                subData = [nextLayer[i] for i in indices[0]]

            if isinstance(subData, list):
                newSubdataForLayer = []
                for i in range(0,len(subData)):
                    newSubdataForLayer = newSubdataForLayer + subData[i].getSubdataStructures(indices[1:])
                return newSubdataForLayer
            else:
                return subData.getSubdataStructures(indices[1:])


    def mergeDataStructures(self, dataStructure, inFront = False):
        '''
        Merges two data structures together.
        The entries of the first data structure will be in front.
        :param dataStructure1: The first data structure
        :param dataStructure2: The second data structure
        :return: The result of the merge operation
        '''

        for entry in self.dataEntries:
            self.dataStructureLocalLayer[entry].mergeDataEntry(dataStructure.dataStructureLocalLayer[entry], inFront)

        self.numElements = self.numElements + dataStructure.numElements

        if self.nextLayer is not None:

            if (inFront):
                self.dataStructureLocalLayer[self.nextLayer] = dataStructure.dataStructureLocalLayer[self.nextLayer] + self.dataStructureLocalLayer[self.nextLayer]
            else:
                self.dataStructureLocalLayer[self.nextLayer] = self.dataStructureLocalLayer[self.nextLayer] + dataStructure.dataStructureLocalLayer[self.nextLayer]



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
            numElements =  [0] * self.dataManager.getMaxDepth()

        numElementsEntry = numElementsLocal
        if (self.isTimeSeries):
            numElementsEntry += 1

        self.numElements = numElementsLocal
        for name, entry in self.dataEntries.items():

            self.dataStructureLocalLayer[name].reserveStorage(numElementsEntry)


        if self.nextLayer is not None and numElements:

            subStructureList = self.dataStructureLocalLayer[self.nextLayer]
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
