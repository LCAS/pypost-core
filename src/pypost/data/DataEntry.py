import numpy as np
from pypost.data.Data import DataType
from scipy.sparse import csr_matrix


class DataEntry():
    '''
    DataEntry stores the properties of a data entry.
    '''

    def __init__(self, name, numDimensions, minRange = None, maxRange = None, isPeriodic = None, dataType = DataType.continuous, takeFromSettings = False):
        '''
        Constructor
        '''
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

    def createDataMatrix(self, numElements):
        if (self.dataType == DataType.continuous):
            return np.zeros((numElements,) + self.numDimensions, dtype=np.float_)
        if (self.dataType == DataType.discrete):
            return np.zeros((numElements,) + self.numDimensions, dtype=np.int_)
        if (self.dataType == DataType.sparse):
            return csr_matrix((numElements, self.numDimensions[0]))

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
