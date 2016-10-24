import unittest
import numpy as np
from pypost.data import DataManager
from pypost.mappings import Mapping, FeatureGenerator

class DummyMapping(Mapping):

    def __init__(self, dataManager):
        Mapping.__init__(self, dataManager, ['X'], ['Y'])

    @Mapping.MappingMethod()
    def dummyFunction(self, X):
        print('Features where called!', X)
        return X**2

class testFeatures(unittest.TestCase):
    def test_generator(self):

        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)
        f = DummyMapping(dataManager)

        features = FeatureGenerator(dataManager, f)

        data = dataManager.getDataObject(10)

        data[...].X = np.random.normal(0,1,(10,1))
        print('Features: ', data[...].Y)
        print('Features: ', data[...].Y)

        data[...].Y_validFlag = np.vstack((np.ones((5,1), dtype=bool), np.zeros((5,1), dtype=bool)))

        print('Features: ', data[...].Y)

