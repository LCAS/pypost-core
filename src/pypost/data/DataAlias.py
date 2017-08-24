from enum import Enum
import numpy as np
import time

class IndexModifierBase():

    def __init__(self):
        self.dimensionMultiplier = 1

    def modifyIndex(self, index, numElements):
        return index


class IndexModifierNext(IndexModifierBase):

    def modifyIndex(self, index, numElements):

        if index == Ellipsis:
            index = slice(1, numElements + 1)
        elif isinstance(index, int):
            index = index + 1
        elif isinstance(index, slice):
            index = slice(index.start + 1, index.stop + 1, index.step)
        elif isinstance(index, list):
            index = [x + 1 for x in index]
        else:
            assert False, 'Index must be Ellipsis, int, int-list or slice'
        return index

class IndexModifierLast(IndexModifierBase):

    def modifyIndex(self, index, numElements):
        if index == Ellipsis:
            index = [0] + list(range(0, numElements - 1))
        elif isinstance(index, int):
            if (index > 0):
                index = index - 1
        elif isinstance(index, slice):
            if (index.start > 0):
                index = slice(index.start - 1, index.stop - 1, index.step)
            else:
                index = [0] + list(range(0, index.stop - 1))
        elif isinstance(index, list):
            index = [x - 1 if x > 0 else 0 for x in index]
        else:
            assert False, 'Index must be Ellipsis, int or slice'
        return index


class IndexModifierAll(IndexModifierBase):

    def modifyIndex(self, index, numElements):
        if index == Ellipsis:
            index = slice(0, numElements + 1)
        return index

class IndexModifierTimeWindow(IndexModifierBase):


    def __init__(self, index1, index2, dropOutSamples = False):
        self.index1 = index1
        self.index2 = index2

        self.dimensionMultiplier = index2 - index1 + 1

        self.rangeArray = np.array(range(self.index1, self.index2 + 1))
        self.rangeArray = self.rangeArray.reshape((self.rangeArray.shape[0], 1))

        self.dropOutSamples = dropOutSamples

    def modifyIndex(self, index, numElements):

        if index == Ellipsis:
            indexSingle = list(range(0, numElements))
        elif isinstance(index, (int, list)):
            indexSingle = [index]
        elif isinstance(index, slice):
            indexSingle = range(index.start, index.stop, index.step)
        else:
            assert False, 'Index must be Ellipsis, int or slice'

        indexSingleArray = np.array(indexSingle, dtype=int)
        if (self.dropOutSamples):

            indexSingleArray = indexSingleArray[indexSingleArray >= - self.index1]
            indexSingleArray = indexSingleArray[indexSingleArray <= numElements - self.index2]


        indexMatrix = np.clip(np.tile(indexSingleArray.reshape((1, indexSingleArray.shape[0])), (self.rangeArray.shape[0], 1)) + self.rangeArray, 0, numElements)
        index = tuple(indexMatrix.tolist())



        return index


class DataAlias():
    '''
    DataAliases are subsets or concatinations of DataEntries.
    '''

    def __init__(self, aliasName, entryList, numDimensions, indexModifier = IndexModifierBase(), useConcatVertical = False):
        '''
        :param aliasName The name of the alias
        :param entryList A list of entry names and the corresponding slices
                         the alias should point to, e.g.
                         [('param', slice(1, 5, 2)), ('param2': ...)]
        '''
        self.name = aliasName
        self.entryList = entryList

        if isinstance(numDimensions, int):
            self.numDimensions = (numDimensions,)
        else:
            self.numDimensions = numDimensions

        self.indexModifier = indexModifier

        self.minRange = None
        self.maxRange = None

        self.useConcatVertical = useConcatVertical

        self.readOnly = False

    def modifyIndex(self, index, numElements):

        return self.indexModifier.modifyIndex(index, numElements)


