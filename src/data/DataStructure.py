import numpy as np
from DataAlias import DataAlias


class DataStructure():
    '''
    DataStructure handles the data structure (containing real data) for the
    data object.
    '''

    def __init__(self):
        '''Constructor'''
        self.dataStructureLocalLayer = dict()

    def __len__(self):
        return len(self.dataStructureLocalLayer)

    def __contains__(self, name):
        return name in self.dataStructureLocalLayer

    def __setitem__(self, name, item):
        if isinstance(item, np.ndarray):
            # item contains 'real' data
            if name not in self.dataStructureLocalLayer:
                # create the new data entry
                self.dataStructureLocalLayer[name] = item
            elif isinstance(self.dataStructureLocalLayer[name], np.ndarray):
                # assigning to a 'real' data entry (a matrix)
                self.dataStructureLocalLayer[name] = item
            elif isinstance(self.dataStructureLocalLayer[name], DataAlias):
                # asssigning to a data alias
                dataAlias = self.dataStructureLocalLayer[name]

                currentIndexInItem = 0

                for entryName, slice_ in dataAlias.entryList:
                    # calculate the dimensions (width) of the current entry
                    l = self[entryName][:, slice_].shape[1]
                    entry = self.dataStructureLocalLayer[entryName]

                    if isinstance(entry, DataAlias):
                        # dataAlias contains another DataAlias (entry)
                        # we have to update it manually (explicit read and
                        # write)
                        entry = self[entryName]
                        entry[:, slice_] = \
                            item[:, currentIndexInItem:currentIndexInItem+l]
                        self[entryName] = entry
                    elif isinstance(entry, np.ndarray):
                        # writing directly to the ndarray...
                        entry[:, slice_] = \
                            item[:, currentIndexInItem:currentIndexInItem+l]
                    else:
                        raise ValueError("Unknown type of the data entry")

                    currentIndexInItem += l
            else:
                raise ValueError("unknown data type:",
                                 type(self.dataStructureLocalLayer[name]))

        else:
            # assigning a definition of an alias or a subDataStructure
            self.dataStructureLocalLayer[name] = item

    def __getitem__(self, name):
        if name not in self.dataStructureLocalLayer:
            raise ValueError("The element '" + str(name) + "' does not exist.")

        if isinstance(self.dataStructureLocalLayer[name], np.ndarray):
            # directly return the data from the data array
            return self.dataStructureLocalLayer[name]
        elif isinstance(self.dataStructureLocalLayer[name], DataAlias):
            # get the data from a DataAlias
            data = None
            dataAlias = self.dataStructureLocalLayer[name]

            for entryName, slice_ in dataAlias.entryList:
                entry = self.dataStructureLocalLayer[entryName]

                if isinstance(entry, DataAlias):
                    # dataAlias contains another DataAlias (entry)
                    entry = self[entryName]
                elif not isinstance(entry, np.ndarray):
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
            raise ValueError("Illegal instance")

    def getDataEntry(self, path, indices):
        '''
        Returns the data points from the required data entry (or
        alias).
        @param path the path to the requested entry as an array.
                    e.g. ['steps', 'subSteps', 'subActions']
        @param indices the hierarchical indices (depending on the hierarchy, it
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
            else:
                return np.array(
                    [self[path[0]][indices[0]]])

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
            else:
                raise ValueError("Invalid data type: indices[0]")

            for subDataStructure in subLayers:
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
        @param path the path to the requested entry as an array.
                    e.g. ['steps', 'subSteps', 'subActions']
        @param indices the hierarchical indices (depending on the hierarchy, it
                       can have different number of elements) as an array.
                       If the number of indices is less than the depth of the
                       hierarchy (less than the length of the path), all other
                       indices will be treated as "...".
                       indices may also be a number which is equivalent to an
                       array containing only one element
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
            elif isinstance(indices[0], slice):
                # set the data for the selected iterations of the requested
                # entry
                indexRange = range(0, indices[0].stop)[indices[0]]
                if len(data.shape) != 2 or data.shape[0] != len(indexRange):
                    raise ValueError("Invalid data format")
                self[path[0]][indices[0]] = data
            elif isinstance(indices[0], int):
                # set the data for a single iteration of the requested entry

                if len(data.shape) == 2:
                    # we only want to store a single vector, not an array
                    # containing only this vector (we want [1, 1] instead of
                    # [[1,1]])

                    if data.shape[0] != 1:
                        raise ValueError('The given data object is a ' +
                                         'matrix, not a vector.')

                    data = data[0]

                self[path[0]][indices[0]] = data
            else:
                raise ValueError("Invalid data type: indices[0]")

        else:
            # set the data in lower layers
            subLayers = None

            if indices[0] == Ellipsis:
                # devide the data into len(subLayers) parts and pass each of
                # these subData's to the corresponding subLayer
                subLayers = self.dataStructureLocalLayer[path[0]]
                subDataLen = int(data.shape[0]/len(subLayers))

                i = 0
                for subDS in subLayers:
                    subData = data[i*subDataLen:(i+1)*subDataLen]
                    subDS.setDataEntry(path[1:], indices[1:], subData)
                    i += 1
            elif isinstance(indices[0], slice):
                subLayers = self.dataStructureLocalLayer[path[0]]
                indexRange = range(0, indices[0].stop)[indices[0]]
                subDataLen = int(data.shape[0]/len(indexRange))
                dataIndex = 0
                for i in indexRange:
                    subData = data[dataIndex:dataIndex+subDataLen]
                    subLayers[i].setDataEntry(path[1:], indices[1:], subData)
                    dataIndex += subDataLen
            else:
                # pass the data to excaltly one lower layer
                subDS = self.dataStructureLocalLayer[path[0]][indices[0]]
                subDS.setDataEntry(path[1:], indices[1:], data)
