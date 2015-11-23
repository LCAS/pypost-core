import unittest
import sys
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

    def test_addDataEntry(self):
        dataManager = DataManager('episodes')
        dataManager.addDataEntry('parameters', 5, -1, 1)

        self.assertIsInstance(dataManager.dataEntries, dict)
        self.assertIsInstance(dataManager.dataEntries['parameters'], DataEntry)
        self.assertEqual(dataManager.dataEntries['parameters'].size, 5)
        self.assertEqual(dataManager.dataEntries['parameters'].minValue, -1)
        self.assertEqual(dataManager.dataEntries['parameters'].maxValue, 1)

    def test_addAlias(self):
        dataManager = DataManager('episodes')
        
        self.assertIsInstance(dataManager.dataAliases, dict)
        
        dataManager.addDataEntry('parameters', 5, -1, 1)
        
        dataManager.addDataAlias('parameterAlias', {'parameters' : slices(0,1)}) 
        self.assertEqual(dataManager.dataAliases['parameterAlias'], DataAlias('subparameters', {'parameters': slices(0, 1)}))
        
        dataManager.addDataAlias('parameterAlias', {'parameters': slices(0, 2)})
        self.assertEqual(dataManager.dataAliases['parameterAlias'], DataAlias({'parameters': slices(0, 1)}))
        

if __name__ == '__main__':
    unittest.main()
