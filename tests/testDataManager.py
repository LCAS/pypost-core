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

        myData = dataManager.getDataObject([10, 5, 1])

        self.assertEqual(len(myData.dataStructure['parameters']), 10)
        self.assertEqual(len(myData.dataStructure['context']), 10)
        self.assertEqual(len(myData.dataStructure['parameters'][0]), 5)
        self.assertEqual(len(myData.dataStructure['parameters'][9]), 5)
        self.assertEqual(len(myData.dataStructure['context'][0]), 2)
        self.assertEqual(len(myData.dataStructure['context'][9]), 2)
        self.assertEqual(len(myData.dataStructure['steps']), 10)
        self.assertEqual(len(myData.dataStructure['steps'][0]), 3)
        self.assertEqual(
            len(myData.dataStructure['steps'][0]['states']), 5)
        self.assertEqual(
            len(myData.dataStructure['steps'][0]['states'][0]), 1)
        self.assertEqual(
            len(myData.dataStructure['steps'][0]['actions']), 5)
        self.assertEqual(
            len(myData.dataStructure['steps'][0]['actions'][0]), 2)
        self.assertEqual(
            len(myData.dataStructure['steps'][0]['actions'][1]), 2)
        self.assertEqual(
            len(myData.dataStructure['steps'][0]['subSteps']), 5)
        self.assertEqual(
            len(myData.dataStructure['steps'][0]['subSteps'][0]
                ['subActions']), 1)
        self.assertEqual(
            len(myData.dataStructure['steps'][0]['subSteps'][0]
                ['subActions']), 1)
        self.assertEqual(
            len(myData.dataStructure['steps'][0]['subSteps'][0]
                ['subActions'][0]), 2)

    def test_addDataEntry(self):
        dataManager = DataManager('episodes')
        dataManager.addDataEntry('parameters', 5, -1 * np.ones(5),
                                 np.array([1, 1, 3, 1, 1]))

        self.assertIsInstance(dataManager.dataEntries, dict)
        self.assertIsInstance(dataManager.dataEntries['parameters'], DataEntry)
        self.assertEqual(dataManager.dataEntries['parameters'].numDimensions,
                         5)
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
        self.assertEqual(dataManager.dataAliases['parameterAlias'].entryList,
                         [('parameters', slice(0, 1))])

        # Replace entry of same alias
        dataManager.addDataAlias('parameterAlias', [('parameters',
                                                    slice(0, 2))])
        self.assertEqual(dataManager.dataAliases['parameterAlias'].entryList,
                         [('parameters', slice(0, 2))])

        # Add another entry to alias
        dataManager.addDataAlias('parameterAlias', [('context', ...)])
        self.assertEqual(dataManager.dataAliases['parameterAlias'].entryList,
                         [('parameters', slice(0, 2)), ('context', ...)])

        # Recursive alias
        dataManager.addDataAlias('aliasToParameterAlias',
                                 [('parameterAlias', ...)])
        self.assertEqual(
            dataManager.dataAliases['aliasToParameterAlias'].entryList,
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
                                  ('context', slice(2, 5))])

        myData = dataManager.getDataObject([10, 5, 1])

        myData.dataStructure['parameters'][:] = np.ones(5)
        myData.dataStructure['context'][:] = np.ones(5)*2

        paramAlias = myData.dataStructure['parameterAlias']
        paramAlias[:] = np.ones(2)*3
        paramAlias[0][1] = 10
        myData.dataStructure['parameterAlias'] = paramAlias

        self.assertEqual(myData.dataStructure['parameters'][0][1], 10)
        self.assertEqual(myData.dataStructure['parameters'][0][2], 1)
        self.assertEqual(myData.dataStructure['parameters'][3][1], 3)
        self.assertEqual(myData.dataStructure['parameters'][5][3], 1)

        twoAlias = myData.dataStructure['twoAlias']
        twoAlias[4] = np.ones(5)*4
        twoAlias[5] = np.ones(5)*5
        twoAlias[6] = np.ones(5)*6
        twoAlias[-1] = np.ones(5)*9

        myData.dataStructure['twoAlias'] = twoAlias

        self.assertEqual(myData.dataStructure['twoAlias'][0][3], 2)
        self.assertEqual(myData.dataStructure['twoAlias'][-1][3], 9)
        self.assertEqual(myData.dataStructure['twoAlias'][4][2], 4)
        self.assertEqual(myData.dataStructure['twoAlias'][5][2], 5)
        self.assertEqual(myData.dataStructure['parameters'][0][0], 3)
        self.assertEqual(myData.dataStructure['parameters'][0][1], 10)
        self.assertEqual(myData.dataStructure['parameters'][0][2], 1)
        self.assertEqual(myData.dataStructure['parameters'][4][2], 1)
        self.assertEqual(myData.dataStructure['parameters'][5][2], 1)
        self.assertEqual(myData.dataStructure['context'][1][3], 2)
        self.assertEqual(myData.dataStructure['context'][6][3], 6)
        self.assertEqual(myData.dataStructure['context'][-1][3], 9)
        self.assertEqual(myData.dataStructure['context'][4][0], 2)
        self.assertEqual(myData.dataStructure['context'][5][1], 2)
        self.assertEqual(myData.dataStructure['context'][4][2], 4)
        self.assertEqual(myData.dataStructure['context'][5][2], 5)

    def test_getAliasAliasData(self):
        # getting the date from an alias that points to an alias
        pass

    def test_reserveStorage(self):
        dataManager = DataManager('episodes')
        dataManager.addDataEntry('parameters', 5)
        dataManager.addDataEntry('context', 2)

        subDataManager = DataManager('steps')
        subDataManager.addDataEntry('states', 2)
        subDataManager.addDataEntry('actions', 2)

        dataManager.subDataManager = subDataManager

        data = dataManager.getDataObject([100, 20])

        data.reserveStorage([20, 20])

        self.assertEqual(data.dataStructure['context'].shape[0], 20)
        self.assertEqual(data.dataStructure['parameters'].shape[0], 20)

        for i in range(0, 20):
            self.assertEqual(data.dataStructure['steps'][i]['states'].shape[0],
                             20)
            self.assertEqual(
                data.dataStructure['steps'][i]['actions'].shape[0], 20)

        data.reserveStorage([50, 100])

        self.assertEqual(data.dataStructure['context'].shape[0], 50)
        self.assertEqual(data.dataStructure['parameters'].shape[0], 50)

        for i in range(0, 50):
            self.assertEqual(
                data.dataStructure['steps'][i]['states'].shape[0], 100)
            self.assertEqual(
                data.dataStructure['steps'][i]['actions'].shape[0], 100)

        data.reserveStorage([50, 0])

        self.assertEqual(data.dataStructure['context'].shape[0], 50)
        self.assertEqual(data.dataStructure['parameters'].shape[0], 50)

        for i in range(0, 50):
            self.assertEqual(
                data.dataStructure['steps'][i]['states'].shape[0], 0)
            self.assertEqual(
                data.dataStructure['steps'][i]['actions'].shape[0], 0)

if __name__ == '__main__':
    unittest.main()
