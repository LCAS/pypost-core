import numpy as np
from DataAlias import DataAlias


class DataStructure():
    '''
    DataStructure handles the date structure (containing real data) for the
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
                    l = len(self.dataStructureLocalLayer[entryName][slice_])
                    self.dataStructureLocalLayer[entryName][slice_] = item[currentIndexInItem:currentIndexInItem+l]
                    currentIndexInItem += l
            else:
                raise ValueError("unknown data type:",
                                 type(self.dataStructureLocalLayer[name]))

        else:
            # assigning a definition of an alias or a subDataStructure
            self.dataStructureLocalLayer[name] = item

    def __getitem__(self, name):
        if isinstance(self.dataStructureLocalLayer[name], np.ndarray):
            # directly return the data from the data array
            return self.dataStructureLocalLayer[name]
        elif isinstance(self.dataStructureLocalLayer[name], DataAlias):
            # get the data from a DataAlias
            data = None
            dataAlias = self.dataStructureLocalLayer[name]

            for entryName, slice_ in dataAlias.entryList:
                # TODO: alias to alias
                if data is None:
                    data = self.dataStructureLocalLayer[entryName][slice_]
                else:
                    entryData = self.dataStructureLocalLayer[entryName][slice_]
                    data = np.concatenate((data, entryData))

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

        if len(path) == 0:
            raise ValueError("Empty paths are not allowed")
        elif len(path) == 1:
            # get the data from the current layer
            if indices[0] == 1:
                return np.array(
                    [self.dataStructureLocalLayer[path[0]][indices[0]]])
            else:
                return self.dataStructureLocalLayer[path[0]][indices[0]]

        else:
            # get the data from lower layers
            data = None
            subLayers = None

            if indices[0] == Ellipsis:
                subLayers = self.dataStructureLocalLayer[path[0]]
            else:
                subLayers = [self.dataStructureLocalLayer[path[0]][indices[0]]]

            for subDataStructure in subLayers:
                subData = subDataStructure.getDataEntry(path[1:], indices[1:])

                if data is None:
                    data = subData
                else:
                    data = np.vstack((data, subData))

            return data
            
