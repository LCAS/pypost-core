import numpy as np


class DataStructure():
    '''
    DataStructure handles the date structure (containing real data) for the
    data object.
    '''

    def __init__(self):
        '''Constructor'''
        self.dataStructureLocalLayer = dict()

        '''
        arr = getDataEntry(['context', 'actins', 'subactions'])

        arr = getDataEntry['context']['action']['subaction']


        arr = dataStructure['context']['action']['subaction'].getData()


        arr[3] = 6
        dataStructure['paramters']['action']['subaction'].setData(arr)
        '''
    def __setitem__(self, name, item):
        if isinstance(item, np.ndarray):
            # item contains 'real' data
            if name not in self.dataStructureLocalLayer:
                # create the new data entry
                self.dataStructureLocalLayer[name] = item
            elif isinstance(self.dataStructureLocalLayer[name], np.ndarray):
                # assigning to a 'real' data entry (a matrix)
                self.dataStructureLocalLayer[name] = item
            elif isinstance(self.dataStructureLocalLayer[name], list):
                # asssigning to a data alias

                currentIndexInItem = 0

                for entryName, slice_ in self.dataStructureLocalLayer[name]:
                    l = len(self.dataStructureLocalLayer[entryName][slice_])
                    self.dataStructureLocalLayer[entryName][slice_] = item[currentIndexInItem:currentIndexInItem+l]
                    currentIndexInItem += l
            else:
                raise ValueError("unknown data type:",
                                 type(self.dataStructureLocalLayer[name]))

        else:
            # assigning a definition of an alias or a subDataStructure
            self.dataStructureLocalLayer[name] = item

    def __len__(self):
        return len(self.dataStructureLocalLayer)

    def __contains__(self, name):
        return name in self.dataStructureLocalLayer

    def __getitem__(self, name):
        if isinstance(self.dataStructureLocalLayer[name], np.ndarray):
            return self.dataStructureLocalLayer[name]
        elif isinstance(self.dataStructureLocalLayer[name], DataStructure):
            return self.dataStructureLocalLayer[name]
        elif isinstance(self.dataStructureLocalLayer[name], list):
            # get the data from a DataAlias
            data = None

            for entryName, slice_ in self.dataStructureLocalLayer[name]:
                # TODO: alias to alias
                if data is None:
                    data = self.dataStructureLocalLayer[entryName][slice_]
                else:
                    data = np.concatenate([data, self.dataStructureLocalLayer[entryName][slice_]])

                #np.concatenate(
                #    [data, self.dataStructureLocalLayer[entryName][slice_]])

            return data
