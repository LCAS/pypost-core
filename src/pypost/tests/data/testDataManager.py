import unittest
import numpy as np
from pypost.data.DataAlias import DataAlias
from pypost.data.DataEntry import DataEntry
from pypost.data.DataManager import DataManager
from pypost.tests import DataUtil


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

    def test_getSubDataManagerForDepth(self):
        dataManager = DataManager('episodes')
        subDataManager = DataManager('steps')
        subSubDataManager = DataManager('subSteps')
        dataManager.subDataManager = subDataManager
        subDataManager.subDataManager = subSubDataManager

        self.assertEqual(dataManager.getSubDataManagerForDepth(0), dataManager)
        self.assertEqual(dataManager.getSubDataManagerForDepth(0), dataManager)
        self.assertEqual(dataManager.getSubDataManagerForDepth(0), dataManager)
        self.assertEqual(dataManager.getSubDataManagerForDepth(1),
                         subDataManager)
        self.assertEqual(dataManager.getSubDataManagerForDepth(2),
                         subSubDataManager)
        self.assertEqual(dataManager.getSubDataManagerForDepth(3), None)

    def test_addDataEntry_after_finalize(self):
        dataManager = DataManager('episodes')
        myData = dataManager.getDataObject(10)
        self.assertRaises(RuntimeError,
                          dataManager.addDataEntry, 'parameters', 5)

    def test_addDataEntry_name_conflict(self):
        dataManager = DataManager('episodes')
        dataManager.addDataEntry('parameters', 5)
        dataManager.addDataAlias('conflict', [('parameters', ...)])
        self.assertRaises(ValueError,
                          dataManager.addDataEntry, 'conflict', 0)

    def test_getDataObject(self):
        dataManager = DataManager('episodes')
        subDataManager = DataManager('steps')
        subSubDataManager = DataManager('subSteps')

        dataManager.subDataManager = subDataManager
        subDataManager.subDataManager = subSubDataManager

        dataManager.addDataEntry('parameters', 5)
        dataManager.addDataEntry('contexts', 2)
        subDataManager.addDataEntry('states', 1)
        subDataManager.addDataEntry('actions', 2)
        subSubDataManager.addDataEntry('subStates', 1)
        subSubDataManager.addDataEntry('subActions', 2)

        myData = dataManager.getDataObject([10, 5, 1])

        self.assertTrue(dataManager.finalized)
        self.assertEqual(len(myData.dataStructure['parameters']), 10)
        self.assertEqual(len(myData.dataStructure['contexts']), 10)
        self.assertEqual(len(myData.dataStructure['parameters'][0]), 5)
        self.assertEqual(len(myData.dataStructure['parameters'][9]), 5)
        self.assertEqual(len(myData.dataStructure['contexts'][0]), 2)
        self.assertEqual(len(myData.dataStructure['contexts'][9]), 2)
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

    def test_getDataObject_twice(self):
        dataManager = DataUtil.createTestManager()
        myData = dataManager.getDataObject([10, 5, 1])
        myData = dataManager.getDataObject([3, 1, 2])

    def test_addDataEntry(self):
        dataManager = DataManager('episodes')
        dataManager.addDataEntry('parameters', 5, -1 * np.ones(5),
                                 np.array([1, 1, 3, 1, 1]))

        self.assertIsInstance(dataManager.dataEntries, dict)
        self.assertIsInstance(dataManager.dataEntries['parameters'], DataEntry)
        self.assertEqual(dataManager.dataEntries['parameters'].numDimensions,
                         (5,))
        self.assertTrue((dataManager.dataEntries['parameters'].minRange ==
                         [-1, -1, -1, -1, -1]).all())
        self.assertTrue((dataManager.dataEntries['parameters'].maxRange ==
                         [1, 1, 3, 1, 1]).all())

    def test_isDataEntry(self):
        dataManager = DataUtil.createTestManager()

        self.assertTrue(dataManager.isDataEntry('parameters'))
        self.assertTrue(dataManager.isDataEntry('contexts'))
        self.assertTrue(dataManager.isDataEntry('subActions'))
        self.assertFalse(dataManager.isDataEntry('notaparameter'))

    def test_getDataEntryDepth(self):
        dataManager = DataUtil.createTestManager()
        self.assertEqual(dataManager.getDataEntryDepth('contexts'), 0)
        self.assertEqual(dataManager.getDataEntryDepth('states'), 1)
        self.assertEqual(dataManager.getDataEntryDepth('subActions'), 2)
        self.assertRaises(ValueError, dataManager.getDataEntryDepth, 'none')

    def test_addDataAlias(self):
        dataManager = DataManager('episodes')

        self.assertIsInstance(dataManager.dataAliases, dict)

        dataManager.addDataEntry('parameters', 5, -1, 1)
        dataManager.addDataEntry('contexts', 5, -1, 1)

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
        dataManager.addDataAlias('parameterAlias', [('contexts', ...)])
        self.assertEqual(dataManager.dataAliases['parameterAlias'].entryList,
                         [('parameters', slice(0, 2)), ('contexts', ...)])

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
                          dataManager.addDataAlias, 'contexts',
                          [('contexts', ...)])

    def test_addDataAlias_missing_data_entry(self):
        dataManager = DataManager('episodes')
        self.assertRaises(ValueError,
                          dataManager.addDataAlias, 'alias', [('none', ...)])

    def test_addDataAlias_after_finalize(self):
        dataManager = DataManager('episodes')
        myData = dataManager.getDataObject([10])
        self.assertRaises(RuntimeError, dataManager.addDataAlias, 'alias', [])

    def test_getDataAlias_non_existing(self):
        dataManager = DataUtil.createTestManager()
        self.assertRaises(ValueError, dataManager.getDataAlias, 'none')

    def test_get_alias_data(self):
        dataManager = DataManager('episodes')
        dataManager.addDataEntry('parameters', 5)
        dataManager.addDataEntry('contexts', 5)
        dataManager.addDataAlias('parameterAlias', [('parameters',
                                                     slice(0, 2))])

        dataManager.addDataAlias('twoAlias',
                                 [('parameters', slice(0, 2)),
                                  ('contexts', slice(2, 5))])

        myData = dataManager.getDataObject([10, 5, 1])

        myData.dataStructure['parameters'] = np.ones((10,5))
        myData.dataStructure['contexts'] = np.ones((10,5)) * 2

        paramAlias = myData.dataStructure['parameterAlias']
        paramAlias[:] = np.ones(2) * 3
        paramAlias[0][1] = 10
        myData.dataStructure['parameterAlias'] = paramAlias

        self.assertEqual(myData.dataStructure['parameters'][0][1], 10)
        self.assertEqual(myData.dataStructure['parameters'][0][2], 1)
        self.assertEqual(myData.dataStructure['parameters'][3][1], 3)
        self.assertEqual(myData.dataStructure['parameters'][5][3], 1)

        twoAlias = myData.dataStructure['twoAlias']
        twoAlias[4] = np.ones(5) * 4
        twoAlias[5] = np.ones(5) * 5
        twoAlias[6] = np.ones(5) * 6
        twoAlias[-1] = np.ones(5) * 9

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
        self.assertEqual(myData.dataStructure['contexts'][1][3], 2)
        self.assertEqual(myData.dataStructure['contexts'][6][3], 6)
        self.assertEqual(myData.dataStructure['contexts'][-1][3], 9)
        self.assertEqual(myData.dataStructure['contexts'][4][0], 2)
        self.assertEqual(myData.dataStructure['contexts'][5][1], 2)
        self.assertEqual(myData.dataStructure['contexts'][4][2], 4)
        self.assertEqual(myData.dataStructure['contexts'][5][2], 5)

    def test_get_alias_alias_data(self):
        # reading and manipulating data from an alias that points to another
        # alias
        dataManager = DataUtil.createTestManager()
        dataManager.addDataAlias('alias1',
                                 [('parameters', slice(2, 5))])
        dataManager.addDataAlias('alias2',
                                 [('parameters', slice(0, 2)),
                                  ('alias1', ...)])

        myData = dataManager.getDataObject([3, 5, 10])

        alias1 = myData.getDataEntry('alias1')
        alias1[0] = [2, 3, 4]
        alias1[2] = [2, 3, 4]
        alias1[2][0] = 22
        myData.setDataEntry('alias1', [], alias1)

        self.assertEqual(myData.dataStructure['parameters'][0][0], 0)
        self.assertEqual(myData.dataStructure['parameters'][0][2], 2)
        self.assertEqual(myData.dataStructure['parameters'][0][4], 4)
        self.assertEqual(myData.dataStructure['parameters'][1][4], 0)
        self.assertEqual(myData.dataStructure['parameters'][2][4], 4)
        self.assertEqual(myData.dataStructure['parameters'][2][2], 22)

        alias2 = myData.getDataEntry('alias2')
        alias2[1] = [0, 1, 2, 3, 4]
        myData.setDataEntry('alias2', [], alias2)

        self.assertEqual(myData.dataStructure['parameters'][1][0], 0)
        self.assertEqual(myData.dataStructure['parameters'][1][3], 3)
        self.assertEqual(myData.dataStructure['parameters'][1][4], 4)
        self.assertEqual(myData.dataStructure['parameters'][0][0], 0)
        self.assertEqual(myData.dataStructure['parameters'][2][4], 4)

    def test_getNumDimensions(self):
        dataManager = DataUtil.createTestManager()

        self.assertEqual(dataManager.getNumDimensions('parameters'), 5)
        self.assertEqual(dataManager.getNumDimensions('contexts'), 1)
        self.assertEqual(dataManager.getNumDimensions(['parameters']), 5)
        self.assertEqual(
            dataManager.getNumDimensions(['parameters', 'contexts']), 6)
        self.assertEqual(dataManager.getNumDimensions('states'), 1)
        self.assertEqual(dataManager.getNumDimensions('subStates'), 1)
        self.assertEqual(dataManager.getNumDimensions(
            ['parameters', 'contexts', 'states', 'subStates']), 8)

        self.assertRaises(ValueError, dataManager.getNumDimensions, 'none')

    def test_getMinRange(self):
        dataManager = DataUtil.createTestManager()
        self.assertTrue(
            (dataManager.getMinRange('parameters') == (-100*np.ones(5))).all())

        self.assertTrue((dataManager.getMinRange(['parameters', 'states']) ==
                         -100*np.ones(6)).all())

        self.assertRaises(ValueError, dataManager.getMinRange, 'none')

        brokenAlias = DataAlias('alias', [('none', ...)], 0)
        dataManager.dataAliases['alias'] = brokenAlias

        self.assertRaises(ValueError, dataManager.getMinRange, 'alias')

    def test_getMaxRange(self):
        dataManager = DataUtil.createTestManager()
        self.assertTrue(
            (dataManager.getMaxRange('parameters') == 100*np.ones(5)).all())

        self.assertTrue((dataManager.getMaxRange(['parameters', 'states']) ==
                         100*np.ones(6)).all())

        self.assertRaises(ValueError, dataManager.getMaxRange, 'none')

        brokenAlias = DataAlias('alias', [('none', ...)], 0)
        dataManager.dataAliases['alias'] = brokenAlias

        self.assertRaises(ValueError, dataManager.getMaxRange, 'alias')

    def test_setRange(self):
        dataManager = DataUtil.createTestManager()
        dataManager.setRange('parameters', -1337*np.ones(5), 1337*np.ones(5))

        self.assertTrue(
            (dataManager.getMaxRange('parameters') == 1337*np.ones(5)).all())

        self.assertTrue(
            (dataManager.getMinRange('parameters') == -1337*np.ones(5)).all())

        self.assertRaises(ValueError, dataManager.setRange, 'parameters',
        -1337*np.ones(3), 1337*np.ones(5))

        self.assertRaises(ValueError, dataManager.setRange, 'parameters',
        -1337*np.ones(5), 1337*np.ones(3))

        self.assertRaises(ValueError, dataManager.setRange, 'parameters',
        -1337*np.ones(3), 1337*np.ones(3))

        self.assertRaises(ValueError, dataManager.setRange, 'notaparameter',
        -1337*np.ones(5), 1337*np.ones(5))

        dataManager.finalize()

        self.assertRaises(RuntimeError, dataManager.setRange, 'parameters',
                          -1337*np.ones(5), 1337*np.ones(5))



    def test_getElementNames(self):
        dataManager = DataUtil.createTestManager()
        self.assertEqual(sorted(dataManager.getEntryNames()),
                         ['actions', 'contexts', 'parameters', 'states',
                          'subActions', 'subStates'])

        dataManager = DataManager('testDM')
        dataManager.addDataEntry('a', 5)
        dataManager.addDataEntry('b', 10)
        self.assertEqual(sorted(dataManager.getEntryNames()),
                         sorted(['a', 'b']))

    def test_getElementNamesLocal(self):
        dataManager = DataUtil.createTestManager()
        self.assertEqual(sorted(dataManager.getEntryNamesLocal()),
                         ['contexts', 'parameters'])

    def test_reserveStorage(self):
        dataManager = DataManager('episodes')
        dataManager.addDataEntry('parameters', 5)
        dataManager.addDataEntry('contexts', 2)

        subDataManager = DataManager('steps')
        subDataManager.addDataEntry('states', 2)
        subDataManager.addDataEntry('actions', 2)

        dataManager.subDataManager = subDataManager

        data = dataManager.getDataObject([100, 20])

        data.reserveStorage([20, 20])

        self.assertEqual(data.dataStructure['contexts'].shape[0], 20)
        self.assertEqual(data.dataStructure['parameters'].shape[0], 20)

        for i in range(0, 20):
            self.assertEqual(
                data.dataStructure['steps'][i]['states'].shape[0], 20)
            self.assertEqual(
                data.dataStructure['steps'][i]['actions'].shape[0], 20)

        data.reserveStorage([50, 100])

        self.assertEqual(data.dataStructure['contexts'].shape[0], 50)
        self.assertEqual(data.dataStructure['parameters'].shape[0], 50)

        for i in range(0, 50):
            self.assertEqual(
                data.dataStructure['steps'][i]['states'].shape[0], 100)
            self.assertEqual(
                data.dataStructure['steps'][i]['actions'].shape[0], 100)

        data.reserveStorage([50, 0])

        self.assertEqual(data.dataStructure['contexts'].shape[0], 50)
        self.assertEqual(data.dataStructure['parameters'].shape[0], 50)

        for i in range(0, 50):
            self.assertEqual(
                data.dataStructure['steps'][i]['states'].shape[0], 0)
            self.assertEqual(
                data.dataStructure['steps'][i]['actions'].shape[0], 0)

        data.reserveStorage(15, ...)

        self.assertEqual(data.dataStructure['contexts'].shape[0], 50)
        self.assertEqual(data.dataStructure['parameters'].shape[0], 50)
        # wont work due to reserveStorage(15) in line 420...
        for i in range(0, 50):
            self.assertEqual(
                data.dataStructure['steps'][i]['states'].shape[0], 15)
            self.assertEqual(
                data.dataStructure['steps'][i]['actions'].shape[0], 15)

if __name__ == '__main__':
    unittest.main()
