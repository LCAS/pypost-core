import unittest
import numpy as np
from pypost.data import DataManager
from pypost.mappings import Mapping

class DummyMapping(Mapping):

    def __init__(self, dataManager):
        Mapping.__init__(self, dataManager, ['X'], ['Y'])

    @Mapping.MappingMethod()
    def dummyFunction(self, X):
        print('Features were called!', X)
        return X**2

class testFeatures(unittest.TestCase):
    def test_generator(self):

        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 2)
        dataManager.addDataEntry('Y', 2)
        f = DummyMapping(dataManager)

        dataManager.addFeatureMapping(f)

        data = dataManager.getDataObject(10)

        # features mapping gets called every time now when we access data.Y
        data[...].X = np.random.normal(0,1,(10,2))
        print('Features: ', data[...].Y)
        print('Features: ', data[...].Y)

        f.setLazyEvaluation(True)
        # mapping gets called only once
        print('Features: ', data[...].Y)
        print('Features: ', data[...].Y)
        print('Features: ', data[...].Y)

        # reset valid Tags
        data[...].Y_validFlag = np.vstack((np.ones((5,1), dtype=bool), np.zeros((5,1), dtype=bool)))
        #Now mapping is only called for the last 5 elements
        print('Features: ', data[...].Y)


