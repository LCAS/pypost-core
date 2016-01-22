import unittest
import sys
import numpy as np

# FIXME we should find a better ways than jsut including all the paths:
# e.g. import from ToolBox.Data, ToolBox.Interfaces
sys.path.append('../../src/')

sys.path.append('../../src/')

sys.path.append('../')


from data.DataAlias import DataAlias
from data.DataEntry import DataEntry
from data.DataManager import DataManager

import DataUtil

from distribution.Mapping import Mapping


class testMapping(unittest.TestCase):

    def test_init(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)

        mapping = Mapping(dataManager, ['X'], 'Y', "TestMapping")

        self.assertIsInstance(mapping, Mapping)
        self.assertEqual(mapping.name, 'TestMapping')

    def txest_getInputVariables(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)

        mapping = Mapping(dataManager, ['X'], 'Y', "TestMapping")

        self.assertEqual(mapping.getInputVariables, ['X'])

    # def getOutputVariable(self):

    def test_addDataEntry_simple_mapping(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 11)
        dataManager.addDataEntry('Y', 11)
        dataManager.finalize()

        data = dataManager.getDataObject(1)

        # functions to map
        valueFunction = lambda numElements, X: sin(X)
        valueFunction.__name__ = 'valueFunction'
        gradientFunction = lambda numElements, X: cos(X)
        gradientFunction.__name__ = 'gradientFunction'

        mapping = Mapping(dataManager, 'X', 'Y', 'TestMapping')
        mapping.addMappingFunction(valueFunction)
        mapping.addMappingFunction(gradientFunction, {'Grad'})

        data.setDataEntry(
            'X', [], np.array([np.linspace(-np.pi, np.pi, 11)]))
        mapping.callDataFunction('valueFunction', data, [])

        Y = myData.getDataEntry('Y')
        dY = functionCollection.callDataFunctionOutput(
            'gradientFunction',
            data, [])

    def test_addDataEntry_name_conflict(self):
        #dataManager = DataManager('episodes')
        #dataManager.addDataEntry('parameters', 5)
        #dataManager.addDataAlias('conflict', [('parameters', ...)])
        # self.assertRaises(ValueError,
        #                  dataManager.addDataEntry, 'conflict', 0)
        pass

if __name__ == '__main__':
    unittest.main()
