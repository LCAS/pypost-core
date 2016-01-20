import unittest
import sys
import numpy as np

sys.path.append('../')
import DataUtil

sys.path.append('../../src/data')
from DataAlias import DataAlias
from DataEntry import DataEntry
from DataManager import DataManager

sys.path.append('../../src/mapping')
from distribution import Mapping


class testMapping(unittest.TestCase):

    def test_init(self):
        dataManager = DataManager('values')
        mapping = Mapping(dataManager, ['X'], 'Y', "TestMapping")

        self.assertIsInstance(mapping, Mapping)
        self.assertEqual(mapping.name, 'episodes')

    def test_addDataEntry_simple_mapping(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)
        dataManager.finalize()

        data = dataManager.getDataObject(11)

        # functions to map
        valueFunction = lambda numElements, X: sin(X)
        valueFunction.__name__ = 'valueFunction'
        gradientFunction = lambda numElements, X: cos(X)
        gradientFunction.__name__ = 'gradientFunction'

        mapping = Mapping(dataManager, 'X', 'Y', 'TestMapping')
        mapping.addMappingFunction(valueFunction)
        mapping.addMappingFunction(gradientFunction, {'Grad'})

        data.setDataEntry('X', linspace(-pi, pi, 11).transpose())
        mapping.callDataFunction('valueFunction', data)

        Y = myData.getDataEntry('Y')
        dY = functionCollection.callDataFunctionOutput(
            'gradientFunction',
            data)

        # self.assertRaises(RuntimeError,
        #                  dataManager.addDataEntry, ('parameters', 5), 0)

    def test_addDataEntry_name_conflict(self):
        #dataManager = DataManager('episodes')
        #dataManager.addDataEntry('parameters', 5)
        #dataManager.addDataAlias('conflict', [('parameters', ...)])
        # self.assertRaises(ValueError,
        #                  dataManager.addDataEntry, 'conflict', 0)
        pass

if __name__ == '__main__':
    unittest.main()
