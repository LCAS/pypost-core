import numpy as np
from pypost.common.SettingsClient import SettingsClient
from scipy.sparse import csr_matrix
from enum import Enum

class DataType(Enum):
    continuous = 1
    discrete  = 2
    sparse = 3


class DataEntry(SettingsClient):
    '''
    DataEntry stores the properties of a data entry.
    '''

    def __init__(self, name, numDimensions, minRange = None, maxRange = None, isPeriodic = None, dataType = DataType.continuous, takeFromSettings = False):
        '''
        Constructor
        '''

        SettingsClient.__init__(self)

        self.name = name
        self.numDimensions = numDimensions
        if (isinstance(self.numDimensions,int)):
            self.numDimensions = (self.numDimensions,)

        if (minRange is None):
            self.minRange = -np.ones(self.numDimensions)
        else:
            self.minRange = minRange

        if (maxRange is None):
            self.maxRange = np.ones(self.numDimensions)
        else:
            self.maxRange = maxRange

        if len(self.maxRange.shape) > 1:
            self.maxRange = np.resize(self.maxRange, (len(self.maxRange), 1))

        if len(self.minRange.shape) > 1:
            self.minRange = np.resize(self.minRange, (len(self.minRange), 1))


        self.dataType = dataType
        if (isPeriodic):
            self.isPeriodic = isPeriodic
        else:
            if (len(self.numDimensions) == 1):
                self.isPeriodic = [False] * self.numDimensions[0]
            else:
                self.isPeriodic = None

        self.takeFromSettings = takeFromSettings
        self.data = None

        self.callBackGetter = None
        self.callBackSetter = None
        self.isFeature = None

        self.isValid = False


    def getEntryFromSettings(self, indices, numElements):
        if indices is Ellipsis:
            numElementsFunc = numElements
        if isinstance(indices, int):
            numElementsFunc = 1
        elif isinstance(indices, list):
            numElementsFunc = len(indices)
        elif isinstance(indices, slice):
            numElementsFunc = indices.stop - indices.start
        singleEntry = self.settings.getProperty(self.name)
        entry = np.tile(singleEntry, (numElementsFunc, 1))
        return entry

    def createDataMatrix(self, numElements):
        if (self.dataType == DataType.continuous):
            self.data = np.zeros((numElements,) + self.numDimensions, dtype=np.float_)
        if (self.dataType == DataType.discrete):
            self.data = np.zeros((numElements,) + self.numDimensions, dtype=np.int_)
        if (self.dataType == DataType.sparse):
            self.data = csr_matrix((numElements, self.numDimensions[0]))

        self.isValid = np.zeros((numElements, 1), dtype=bool)

    def reserveStorage(self, numElementsEntry):
        currentSize = self.data.shape[0]
        if currentSize < numElementsEntry:
            self.data = np.vstack((self.data, np.zeros((numElementsEntry - currentSize, self.numDimensions[0]))))
            self.isValid = np.vstack((self.isValid, np.zeros((numElementsEntry - currentSize, 1), dtype=bool)))
        else:
            self.data = np.delete(self.data, slice(numElementsEntry, None, None), 0)
            self.isValid = np.delete(self.isValid, slice(numElementsEntry, None, None), 0)

    def mergeDataEntry(self, dataEntry, inFront):

        if inFront:
            self.data = np.vstack((dataEntry.data, self.data))
            self.isValid = np.vstack((dataEntry.isValid, self.isValid))

        else:
            self.data = np.vstack((self.data, dataEntry.data))
            self.isValid = np.vstack((self.isValid, dataEntry.isValid))

    def isCorrectDataType(self, data):

        if not (isinstance(data, (int, float, np.ndarray, csr_matrix))):
            raise ValueError('Unknown data type!')

        if self.dataType == DataType.continuous:
            return True

        if self.dataType == DataType.discrete:
            if data.dtype == np.int_:
                return True
            else:
                raise ValueError('DataEntry ' + self.name + ' is discrete, please only use integers')


        if self.dataType == DataType.sparse:
            if isinstance(data, csr_matrix):
                return True
            else:
                raise ValueError('DataEntry ' + self.name + ' is discrete, please only use integers')
