import unittest
import sys
import numpy as np
sys.path.append('../src/data')
from DataEntry import DataEntry
from DataManager import DataManager


class testDataManager(unittest.TestCase):

    def test_init(self):
        dataManager = DataManager('episodes')
        self.assertIsInstance(dataManager, DataManager)
        self.assertEqual(dataManager.name, 'episodes')

    def test_subDataManager(self):
        dataManager = DataManager('episodes')
        subDataManager = DataManager('steps')
        subSubDataManager = DataManager('subSteps')

        dataManager.subDataManager = subDataManager
        subDataManager.subDataManager = subSubDataManager

        self.assertIs(dataManager.subDataManager, subDataManager)
        self.assertIs(dataManager.subDataManager.subDataManager,
                      subSubDataManager)

        dataManager.addDataEntry('parameters', 5)
        dataManager.addDataEntry('context', 2)
        subDataManager.addDataEntry('states', 1)
        subDataManager.addDataEntry('actions', 2)
        subSubDataManager.addDataEntry('subStates', 1)
        subSubDataManager.addDataEntry('subActions', 2)

        dataManager.getDataObject([10, 5, 1])

    def test_addDataEntry(self):
        dataManager = DataManager('episodes')
        dataManager.addDataEntry('parameters', 5, -1 * np.ones(5),
                                 np.array([1, 1, 3, 1, 1]))

        self.assertIsInstance(dataManager.dataEntries, dict)
        self.assertIsInstance(dataManager.dataEntries['parameters'], DataEntry)
        self.assertEqual(dataManager.dataEntries['parameters'].size, 5)
        self.assertTrue((dataManager.dataEntries['parameters'].minRange ==
                         [-1, -1, -1, -1, -1]).all())
        self.assertTrue((dataManager.dataEntries['parameters'].maxRange ==
                         [1, 1, 3, 1, 1]).all())

    def test_addAlias(self):
        dataManager = DataManager('episodes')

        self.assertIsInstance(dataManager.dataAliases, dict)

        dataManager.addDataEntry('parameters', 5, -1, 1)
        dataManager.addDataEntry('context', 5, -1, 1)

        dataManager.addDataAlias('parameterAlias', {'parameters':
                                                    slice(0, 1)})

        self.assertEqual(dataManager.dataAliases['parameterAlias'].entryList,
                         {'parameters': slice(0, 1)})

        dataManager.addDataAlias('parameterAlias', {'parameters':
                                                    slice(0, 2)})

        self.assertEqual(dataManager.dataAliases['parameterAlias'].entryList,
                         {'parameters': slice(0, 2)})
        
        dataManager.addDataAlias('parameterAlias', {'context': ...})
        
        self.assertEqual(dataManager.dataAliases['parameterAlias'].entryList, {'parameters': slice(0, 2), 'context': ...})

if __name__ == '__main__':
    unittest.main()
