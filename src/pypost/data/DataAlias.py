from enum import Enum

class IndexModifier(Enum):
    none = 1
    next = 2
    last = 3
    all = 4

class DataAlias():
    '''
    DataAliases are subsets or concatinations of DataEntries.
    '''

    def __init__(self, aliasName, entryList, numDimensions, indexModifier = IndexModifier.none):
        '''
        :param aliasName The name of the alias
        :param entryList A list of entry names and the corresponding slices
                         the alias should point to, e.g.
                         [('param', slice(1, 5, 2)), ('param2': ...)]
        '''
        self.name = aliasName
        self.entryList = entryList
        self.numDimensions = numDimensions
        self.indexModifier = indexModifier

        self.minRange = None
        self.maxRange = None

    def modifyIndex(self, index, numElements):
        if self.indexModifier == IndexModifier.none:
           return index

        if self.indexModifier == IndexModifier.next:
            if index == Ellipsis:
                index = slice(1,numElements + 1)
            elif isinstance(index, int):
                index = index + 1
            elif isinstance(index, slice):
                index = slice(index.start() + 1, index.stop() + 1, index.step())
            elif isinstance(index, int):
                index = [x + 1 for x in index]
            else:
                assert False, 'Index must be Ellipsis, int, int-list or slice'
            return index


        if self.indexModifier == IndexModifier.last:
            if index == Ellipsis:
                index = [0] + list(range(0, numElements-1))
            elif isinstance(index, int):
                if (index > 0):
                    index = index  - 1
            elif isinstance(index, slice):
                if (index.start() > 0):
                    index = slice(index.start() - 1, index.stop() - 1, index.step())
                else:
                    [0] + list(range((0, index.stop() - 1)))
            elif isinstance(index, int):
                index = [x - 1 if x > 0 else 0 for x in index]
            else:
                assert False, 'Index must be Ellipsis, int or slice'
            return index

        if self.indexModifier == IndexModifier.all:
            if index == Ellipsis:
                index = slice(0, numElements + 1)
            return index
