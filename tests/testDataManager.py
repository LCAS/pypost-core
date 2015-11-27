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

    def test_getDataObject(self):
        dataManager = DataManager('episodes')
        subDataManager = DataManager('steps')
        subSubDataManager = DataManager('subSteps')

        dataManager.subDataManager = subDataManager
        subDataManager.subDataManager = subSubDataManager

        dataManager.addDataEntry('parameters', 5)
        dataManager.addDataEntry('context', 2)
        subDataManager.addDataEntry('states', 1)
        subDataManager.addDataEntry('actions', 2)
        subSubDataManager.addDataEntry('subStates', 1)
        subSubDataManager.addDataEntry('subActions', 2)

        dataObject = dataManager.getDataObject([10, 5, 1])

        self.assertEqual(len(dataObject.dataStructure['parameters']), 10)
        self.assertEqual(len(dataObject.dataStructure['context']), 10)
        self.assertEqual(len(dataObject.dataStructure['parameters'][0]), 5)
        self.assertEqual(len(dataObject.dataStructure['parameters'][9]), 5)
        self.assertEqual(len(dataObject.dataStructure['context'][0]), 2)
        self.assertEqual(len(dataObject.dataStructure['context'][9]), 2)
        self.assertEqual(len(dataObject.dataStructure['steps']), 3)
        self.assertEqual(len(dataObject.dataStructure['steps']['states']), 5)
        self.assertEqual(len(dataObject.dataStructure['steps']['states'][0]),
                         1)
        self.assertEqual(len(dataObject.dataStructure['steps']['actions']), 5)
        self.assertEqual(len(dataObject.dataStructure['steps']['actions'][0]),
                         2)
        self.assertEqual(len(dataObject.dataStructure['steps']['actions'][1]),
                         2)
        self.assertEqual(len(dataObject.dataStructure['steps']['subSteps']
                             ['subActions']), 1)
        self.assertEqual(len(dataObject.dataStructure['steps']['subSteps']
                             ['subActions'][0]), 2)

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

        # Add alias
        dataManager.addDataAlias('parameterAlias', [('parameters',
                                                    slice(0, 1))])
        self.assertEqual(dataManager.dataAliases['parameterAlias'],
                         [('parameters', slice(0, 1))])

        # Replace entry of same alias
        dataManager.addDataAlias('parameterAlias', [('parameters',
                                                    slice(0, 2))])
        self.assertEqual(dataManager.dataAliases['parameterAlias'],
                         [('parameters', slice(0, 2))])

        # Add another entry to alias
        dataManager.addDataAlias('parameterAlias', [('context', ...)])
        self.assertEqual(dataManager.dataAliases['parameterAlias'],
                         [('parameters', slice(0, 2)), ('context', ...)])

        # Recursive alias
        dataManager.addDataAlias('aliasToParameterAlias',
                                 [('parameterAlias', ...)])
        self.assertEqual(dataManager.dataAliases['aliasToParameterAlias'],
                         [('parameterAlias', ...)])

        # Alias cycle
        dataManager.addDataAlias('badAlias', [('aliasToParameterAlias', ...)])
        self.assertRaises(ValueError,
                          dataManager.addDataAlias,
                          'aliasToParameterAlias', [('badAlias', ...)])
        self.assertRaises(ValueError,
                          dataManager.addDataAlias, 'badAlias',
                          [('badAlias', ...)])
        self.assertRaises(ValueError,
                          dataManager.addDataAlias, 'context',
                          [('context', ...)])


    def test_getAliasData(self):
        dataManager = DataManager('episodes')
        dataManager.addDataEntry('parameters', 5)
        dataManager.addDataEntry('context', 5)
        dataManager.addDataAlias('parameterAlias', [('parameters',
                                                    slice(0, 2))])

        dataManager.addDataAlias('twoAlias',
                                 [('parameters', slice(0, 2)),
                                  ('context', slice(4, -1))])

        dataObject = dataManager.getDataObject([10, 5, 1])

        dataObject.dataStructure['context'][:] = np.ones(5)*2
        dataObject.dataStructure['parameters'][:] = np.ones(5)

        paramAlias = dataObject.dataStructure['parameterAlias']
        paramAlias[0] = np.ones(5)*3
        paramAlias[0][2] = 10
        dataObject.dataStructure['parameterAlias'] = paramAlias

        self.assertEqual(dataObject.dataStructure['parameters'][0][1], 3)
        self.assertEqual(dataObject.dataStructure['parameters'][0][2], 10)

        twoAlias = dataObject.dataStructure['twoAlias']
        print("twoAlias", twoAlias)
        twoAlias[0] = np.ones(5)*4
        twoAlias[1] = np.ones(5)*5
        twoAlias[2] = np.ones(5)*6
        twoAlias[-1] = np.ones(5)*7

        print("twoAlias", twoAlias)
        dataObject.dataStructure['twoAlias'] = twoAlias

        self.assertEqual(dataObject.dataStructure['twoAlias'][0][3], 4)
        self.assertEqual(dataObject.dataStructure['twoAlias'][-1][3], 7)
        self.assertEqual(dataObject.dataStructure['parameters'][0][3], 4)
        self.assertEqual(dataObject.dataStructure['parameters'][1][3], 5)
        self.assertEqual(dataObject.dataStructure['context'][4][3], 6)
        self.assertEqual(dataObject.dataStructure['context'][-2][3], 7)

        # TODO: remove print()s
        print("parameters", dataObject.dataStructure['parameters'])
        print("context", dataObject.dataStructure['context'])
        print("parameterAlias", dataObject.dataStructure['parameterAlias'])
        print("twoAlias", dataObject.dataStructure['twoAlias'])

    def test_getAliasAliasData(self):
        # getting the date from an alias that points to an alias
        pass

if __name__ == '__main__':
    unittest.main()
