import unittest
import numpy as np

from pypost.data import DataManager, DataType
from pypost.tests import DataUtil
from scipy.sparse import csr_matrix

class testDataManager(unittest.TestCase):

    def test_assert(self):
        dataManager = DataUtil.createTestManager()
        data = dataManager.createDataObject([10, 20, 30])

        self.assertRaises(ValueError, data.setDataEntry, 'parameters', ...,
                          None)

    def test_completeLayerIndex(self):
        dataManager = DataUtil.createTestManager()
        data = dataManager.createDataObject([10, 20, 30])

        self.assertEqual(data.completeLayerIndex(0, ...),
                         [slice(0, 10, None)])

        self.assertEqual(data.completeLayerIndex(2, [..., slice(0, 5)]),
                         [slice(0, 10, None), slice(0, 5, None),
                          slice(0, 30, None)])

        self.assertEqual(data.completeLayerIndex(2, ...),
                         [slice(0, 10, None), slice(0, 20, None),
                          slice(0, 30, None)])

        self.assertEqual(data.completeLayerIndex(1, [..., ..., ...]),
                         [slice(0, 10, None), slice(0, 20, None)])

    def test_getDataEntryDimensions(self):
        dataManager = DataManager('episodes')
        subDataManager = DataManager('steps')
        subSubDataManager = DataManager('subSteps')

        dataManager.subDataManager = subDataManager
        subDataManager.subDataManager = subSubDataManager

        dataManager.addDataEntry('parameters', 5)
        subDataManager.addDataEntry('states', 1)
        subSubDataManager.addDataEntry('subStates', 1)
        subSubDataManager.addDataEntry('subActions', 2)

        myData = dataManager.createDataObject([10, 5, 3])

        self.assertEqual(myData.getDataEntry(['parameters']).shape[0], 10)

        self.assertEqual(
            myData.getDataEntry(['parameters'], [...]).shape[0], 10)

        self.assertEqual(
            myData.getDataEntry(['parameters'], [1]).shape[0], 1)

        self.assertEqual(
            myData.getDataEntry(['steps', 'states'], [1]).shape[0], 5)

        self.assertEqual(
            myData.getDataEntry(['steps', 'states'], [3]).shape[0], 5)

        self.assertEqual(
            myData.getDataEntry(['steps', 'states'],
                                [..., 1]).shape[0], 10)

        self.assertEqual(
            myData.getDataEntry(['steps', 'states'],
                                [..., ...]).shape[0], 50)

        self.assertEqual(
            myData.getDataEntry(['steps', 'states']).shape[0], 50)

        self.assertEqual(
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                [..., ..., ...]).shape[0], 150)

        self.assertEqual(
            myData.getDataEntry(
                ['steps', 'subSteps', 'subActions']).shape[0], 150)

        self.assertEqual(
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                [..., ..., 1]).shape[0], 50)

        self.assertEqual(
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                [..., 1, ...]).shape[0], 30)

        self.assertEqual(
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                [..., 1]).shape[0], 30)

        self.assertEqual(
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                [..., 1, 1]).shape[0], 10)

        self.assertEqual(
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                [1, ..., ...]).shape[0], 15)

        self.assertEqual(
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                [1]).shape[0], 15)

        self.assertEqual(
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                1).shape[0], 15)

        self.assertEqual(
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                [1, ..., 1]).shape[0], 5)

        self.assertEqual(
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                [1, 1, ...]).shape[0], 3)

        self.assertEqual(
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                [1, 1, 1]).shape[0], 1)

    def test_setgetDataEntryLocalLayer(self):
        dataManager = DataManager('episodes')
        dataManager.addDataEntry('parameters', 5, -5, 5)

        myData = dataManager.createDataObject([10])

        # set the data for the parameters of all episodes
        myData.setDataEntry(['parameters'], [], np.ones((10, 5)))
        myData.setDataEntry(['parameters'], [slice(0, 5)], np.ones((5, 5)))

        # the first episode should have different parameters
        myData.setDataEntry(['parameters'], [0], np.array([1, 2, 3, 4, 5]))

        self.assertTrue((myData.dataStructure['parameters'][0] ==
                         np.array([1, 2, 3, 4, 5])).all())
        self.assertTrue((myData.dataStructure['parameters'][1] ==
                         np.array([1, 1, 1, 1, 1])).all())
        self.assertTrue((myData.dataStructure['parameters'][9] ==
                         np.array([1, 1, 1, 1, 1])).all())

        # this should not change anything
        myData.setDataEntry(['parameters'], [], np.ones((10, 5)))
        myData.setDataEntry(['parameters'], [0], np.array([1, 2, 3, 4, 5]))

        self.assertTrue((myData.dataStructure['parameters'][0] ==
                         np.array([1, 2, 3, 4, 5])).all())
        self.assertTrue((myData.dataStructure['parameters'][1] ==
                         np.array([1, 1, 1, 1, 1])).all())
        self.assertTrue((myData.dataStructure['parameters'][9] ==
                         np.array([1, 1, 1, 1, 1])).all())

        # tests for getDataEntry
        self.assertTrue((myData.getDataEntry('parameters') ==
                         myData.dataStructure['parameters']).all())

        self.assertTrue((myData.getDataEntry('parameters', ...) ==
                         myData.dataStructure['parameters']).all())

        self.assertTrue((myData.getDataEntry('parameters')[4] ==
                         myData.dataStructure['parameters'][4]).all())

        self.assertTrue((myData.getDataEntry('parameters', [4]) ==
                         myData.dataStructure['parameters'][4]).all())

    def test_setgetDataEntry(self):
        dataManager = DataManager('episodes')
        subDataManager = DataManager('steps')
        subSubDataManager = DataManager('subSteps')

        dataManager.subDataManager = subDataManager
        subDataManager.subDataManager = subSubDataManager

        subSubDataManager.addDataEntry('subActions', 2, -10, 10)

        myData = dataManager.createDataObject([10, 5, 3])

        # set the data for all subActions of all episodes, steps and subSteps
        myData.setDataEntry(['steps', 'subSteps', 'subActions'],
                            [], np.ones((150, 2)))

        # all subActions in the 3rd subSteps of all steps of the 2nd episode
        # should have different parameters
        myData.setDataEntry(['steps', 'subSteps', 'subActions'],
                            [1, ..., 2], np.array([
                                [2, 1],
                                [2, 2],
                                [2, 3],
                                [2, 4],
                                [2, 5]]))

        self.assertTrue((myData.dataStructure['steps'][0]['subSteps'][0]
                         ['subActions'][0] == np.array([1, 1])).all())

        self.assertTrue((myData.dataStructure['steps'][1]['subSteps'][1]
                         ['subActions'][1] == np.array([1, 1])).all())

        self.assertTrue((myData.dataStructure['steps'][9]['subSteps'][4]
                         ['subActions'][2] == np.array([1, 1])).all())

        self.assertTrue((myData.dataStructure['steps'][1]['subSteps'][4]
                         ['subActions'][1] == np.array([1, 1])).all())

        self.assertTrue((myData.dataStructure['steps'][1]['subSteps'][0]
                         ['subActions'][2] == np.array([2, 1])).all())

        self.assertTrue((myData.dataStructure['steps'][1]['subSteps'][4]
                         ['subActions'][2] == np.array([2, 5])).all())

        # tests for getDataEntry
        self.assertTrue((
            myData.getDataEntry(['steps', 'subSteps', 'subActions'], [0, 0]) ==
            myData.dataStructure['steps'][0]['subSteps'][0]['subActions']
        ).all())

        self.assertTrue((
            myData.getDataEntry(['steps', 'subSteps', 'subActions'], 1) ==
            np.array([[1, 1], [1, 1], [2, 1],
                      [1, 1], [1, 1], [2, 2],
                      [1, 1], [1, 1], [2, 3],
                      [1, 1], [1, 1], [2, 4],
                      [1, 1], [1, 1], [2, 5]])
        ).all())

        self.assertTrue((
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                [1, ..., 2]) ==
            np.array([[2, 1], [2, 2], [2, 3], [2, 4], [2, 5]])
        ).all())

        self.assertTrue((
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                [1, 3, 2]) ==
            np.array([[2, 4]])
        ).all())

        self.assertTrue((
            myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                [2, 3, 2]) ==
            np.array([[1, 1]])
        ).all())

        # all subActions in every second subStep of all steps of the 2nd episode
        # should have different parameters
        myData.setDataEntry(['steps', 'subSteps', 'subActions'],
                            [1, slice(0, 5, 2), 2], np.array([
                                [3, 1],
                                [3, 2],
                                [3, 3]]))

        self.assertTrue((
            myData.getDataEntry(['steps', 'subSteps', 'subActions'], 1) ==
            np.array([[1, 1], [1, 1], [3, 1],
                      [1, 1], [1, 1], [2, 2],
                      [1, 1], [1, 1], [3, 2],
                      [1, 1], [1, 1], [2, 4],
                      [1, 1], [1, 1], [3, 3]])
        ).all())

        # all subActions in the first 3 subSteps of all steps of the 2nd episode
        # should have different parameters
        myData.setDataEntry(['steps', 'subSteps', 'subActions'],
                            [1, slice(0, -2), 2], np.array([
                                [4, 1],
                                [4, 2],
                                [4, 3]]))

        self.assertTrue((
            myData.getDataEntry(['steps', 'subSteps', 'subActions'], 1) ==
            np.array([[1, 1], [1, 1], [4, 1],
                      [1, 1], [1, 1], [4, 2],
                      [1, 1], [1, 1], [4, 3],
                      [1, 1], [1, 1], [2, 4],
                      [1, 1], [1, 1], [3, 3]])
        ).all())

        self.assertRaises(ValueError, myData.setDataEntry,
                          ['steps', 'subSteps', 'subActions'],
                          [1, 2, slice(0, 1)], np.array([[5, 1], [5, 2]]))

        self.assertRaises(ValueError, myData.setDataEntry,
                          ['steps', 'subSteps', 'subActions'],
                          [1, ..., 0], np.array([[5, 1], [5, 2], [5, 3]]))

        self.assertRaises(ValueError, myData.setDataEntry,
                          ['steps', 'subSteps', 'subActions'],
                          [1, slice(0, -2), 2], np.array([[5, 1], [5, 2]]))

        self.assertRaises(ValueError, myData.setDataEntry,
                          ['steps', 'subSteps', 'subActions'],
                          [1, slice(0, -2), 2], np.array([]))

        self.assertRaises(ValueError, myData.setDataEntry,
                          ['steps', 'subSteps', 'subActions'],
                          [1, slice(0, -2), 2], np.array([
                              [5, 1], [5, 2], [5, 3], [5, 4]]))

    def test_setgetDataEntryRanges(self):
        dataManager = DataManager('episodes')
        dataManager.addDataEntry('parameters', 5)  # implicit ranges ([-1 1])
        dataManager.addDataEntry('temperature', 24, -20, 100)

        myData = dataManager.createDataObject([10, 5, 3])

        # this should not raise any exception
        myData.setDataEntry(['parameters'], [], np.ones((10, 5)))
        myData.setDataEntry(['parameters'], [], -np.ones((10, 5)))
        myData.setDataEntry(
            ['parameters'], [slice(0, 5)], 0.97 * np.ones((5, 5)))
        myData.setDataEntry(
            ['parameters'], [slice(0, 5)], -0.5 * np.ones((5, 5)))
        myData.setDataEntry('temperature', [], -20 * np.ones((10, 24)))
        myData.setDataEntry('temperature', [], -19 * np.ones((10, 24)))
        myData.setDataEntry('temperature', [], 99 * np.ones((10, 24)))
        myData.setDataEntry('temperature', [], np.zeros((10, 24)))

        #self.assertRaises(ValueError, myData.setDataEntry, 'parameters', [],
        #                  -2 * np.ones((10, 5)), True)
        #self.assertRaises(ValueError, myData.setDataEntry, 'parameters', [],
        #                  1.1 * np.ones((10, 5)), True)
        #self.assertRaises(ValueError, myData.setDataEntry, ['temperature'], [],
        #                  111 * np.ones((10, 5)), True)
        #self.assertRaises(ValueError, myData.setDataEntry, ['temperature'], [],
        #                  -9999999 * np.ones((10, 5)), True)

    def test_setgetDataEntryAlias(self):
        dataManager = DataUtil.createTestManager()
        dataManager.addDataAlias('statesAlias', [('states', ...)])
        dataManager.addDataAlias('pcAlias', [('parameters', ...),
                                             ('contexts', ...)])

        data = dataManager.createDataObject([10, 20, 30])

        self.assertTrue('statesAlias' in dataManager.getAliasNames() and
                        'pcAlias' in dataManager.getAliasNames())

        data.setDataEntry('states', [], np.ones((200, 1)))

        self.assertTrue((data.getDataEntry('statesAlias', []) ==
                         np.ones((200, 1))).all())

        data.setDataEntry('statesAlias', [], np.zeros((200, 1)))

        self.assertTrue((data.getDataEntry('states', []) ==
                         np.zeros((200, 1))).all())

        data.setDataEntry('parameters', [], np.ones((10, 5)))
        data.setDataEntry('contexts', [], np.ones((10, 1)))

        self.assertTrue((data.getDataEntry('pcAlias', []) ==
                         np.ones((10, 6))).all())

        data.setDataEntry('pcAlias', slice(0,10), np.zeros((10, 6)))

        self.assertTrue((data.getDataEntry('parameters', []) ==
                         np.zeros((10, 5))).all())
        self.assertTrue((data.getDataEntry('contexts', []) ==
                         np.zeros((10, 1))).all())

    def test_getDataEntryDeepCopy(self):
        dataManager = DataManager('episodes')
        subDataManager = DataManager('steps')
        subSubDataManager = DataManager('subSteps')

        dataManager.subDataManager = subDataManager
        subDataManager.subDataManager = subSubDataManager

        dataManager.addDataEntry('parameters', 5)
        subDataManager.addDataEntry('states', 1)
        subSubDataManager.addDataEntry('subActions', 2, -10, 10)

        myData = dataManager.createDataObject([1, 1, 1])

        # set the data for all subActions of all episodes, steps and subSteps
        myData.setDataEntry('subActions', [], np.ones((1, 2)))

        self.assertTrue((myData.dataStructure['steps'][0]['subSteps'][0]
                         ['subActions'][0] == np.array([1, 1])).all())

        data1 = myData.getDataEntry('subActions', [])
        data2 = myData.getDataEntry('subActions', [], True)
        data3 = myData.getDataEntry('subActions', [], False)
        data4 = myData.getDataEntry('subActions', [], False)

        self.assertTrue((data1 == data2).all())
        self.assertTrue((data2 == data3).all())
        self.assertTrue((data3 == data4).all())

        data2[0, 1] = 7  # This should NOT have any impact on any other data

        self.assertTrue((data2 != data1).any())
        self.assertTrue((data2 != data3).any())
        self.assertTrue((data2 != data4).any())

        data5 = myData.getDataEntry('subActions', [])

        data3[0, 0] = 8  # This MAY impact the data in the data structure,
        # but should not impact data1 or data2

        self.assertTrue((data5 == data1).all())
        self.assertTrue((data3 != data1).any())
        self.assertTrue((data3 == data4).any())

        myData.setDataEntry(
            'subActions',
            [],
            data2)  # still no impact on data1
        self.assertTrue((data5 == data1).all())
        self.assertTrue(((myData.getDataEntry('subActions', [])) ==
                         [1, 7]).all())

    def test_getDataEntryList(self):
        dataManager = DataManager('episodes')
        dataManager.addDataEntry('parameters', 5)
        dataManager.addDataEntry('contexts', 3)
        myData = dataManager.createDataObject([10])

        # set the data for the parameters and context of all episodes
        myData.setDataEntry(['parameters'], [...], np.ones((10, 5)))
        myData.setDataEntry(['contexts'], [...], np.ones((10, 3)))

        result = myData.getDataEntryList(['parameters', 'contexts'], [...])

        self.assertTrue(isinstance(result, list))
        self.assertTrue((result[0] == np.ones((10, 5))).all())
        self.assertTrue((result[1] == np.ones((10, 3))).all())

        result = myData.getDataEntryList([('parameters', 'contexts')], [...])

        self.assertEqual(len(result), 1)
        self.assertTrue((result[0] == np.ones((10, 8))).all())

    def test_set_data_entry_int(self):
        manager = DataUtil.createTestManager()
        data = manager.createDataObject([10, 20, 30])
        data.setDataEntry('parameters', 1, np.ndarray((5)))

    def testMatrixEntries(self):
        manager = DataManager('episodes')
        manager.addDataEntry('matrixEntry', (10,10))

        data = manager.createDataObject(5)

        data.setDataEntry('matrixEntry', slice(0,2), np.ones((2, 10, 10)))
        testMatrix = np.zeros((5,10,10))
        testMatrix[slice(0,2)] = np.ones((2, 10, 10))

        testMatrix = testMatrix - data.getDataEntry('matrixEntry')
        self.assertTrue((testMatrix == 0).all())

    def testIntEntries(self):
        manager = DataManager('episodes')
        manager.addDataEntry('matrixEntry', 10, dataType=DataType.discrete)

        data = manager.createDataObject(5)

        data.setDataEntry('matrixEntry', slice(0,2), np.ones((2, 10), dtype=np.int_))
        testMatrix = np.zeros((5,10))
        testMatrix[slice(0,2)] = np.ones((2, 10))

        testMatrix = testMatrix - data.getDataEntry('matrixEntry')
        self.assertTrue((testMatrix == 0).all())

        #self.assertRaises(ValueError, data.setDataEntry('matrixEntry', slice(0,2), np.ones((2, 10))), True)

    def testSparseEntries(self):
        manager = DataManager('episodes')
        manager.addDataEntry('matrixEntry', 10, dataType=DataType.sparse)

        data = manager.createDataObject(5)

        sparseMatrix = csr_matrix((2,10))
        sparseMatrix[0,4] = 4
        sparseMatrix[1, 2] = 1

        data.setDataEntry('matrixEntry', slice(0, 2), sparseMatrix)
        testMatrix = csr_matrix((5,10))
        testMatrix[slice(0, 2)] = sparseMatrix

        testMatrix = testMatrix - data.getDataEntry('matrixEntry')
        self.assertTrue(np.abs(testMatrix).sum() == 0)

    def test_setDataEntryList(self):
        dataManager = DataManager('episodes')
        dataManager.addDataEntry('parameters', 5, -10, 10)
        dataManager.addDataEntry('contexts', 3, -10, 10)
        myData = dataManager.createDataObject([10])

        # set the data for the parameters and context of all episodes
        myData.setDataEntry(['parameters'], [...], np.ones((10, 5)))
        myData.setDataEntry(['contexts'], [...], np.ones((10, 3)))

        myData.setDataEntryList(['parameters', 'contexts'], [...],
                                [np.zeros((10, 5)), np.zeros((10, 3))])

        self.assertTrue((myData.getDataEntry('parameters', [...]) ==
                         np.zeros((10, 5))).all())
        self.assertTrue((myData.getDataEntry('contexts', [...]) ==
                         np.zeros((10, 3))).all())

        myData.setDataEntryList([('parameters', ['contexts'])], [...],
                                [np.hstack((np.ones((10, 5)), 2 * np.ones((10, 3))))])

        self.assertTrue((myData.getDataEntry('parameters', [...]) ==
                         np.ones((10, 5))).all())
        self.assertTrue((myData.getDataEntry('contexts', [...]) ==
                         2 * np.ones((10, 3))).all())

        myData.setDataEntryList([('parameters', ['contexts'])], [...],
                                [6 * np.ones((10, 8))])

        self.assertTrue((myData.getDataEntry('parameters', [...]) ==
                         6 * np.ones((10, 5))).all())
        self.assertTrue((myData.getDataEntry('contexts', [...]) ==
                         6 * np.ones((3))).all())

        myData.setDataEntryList([('parameters', ['contexts'])], [3],
                                7 * np.ones((1, 8)))

        self.assertTrue((myData.getDataEntry('parameters', [3]) ==
                         7 * np.ones((5))).all())
        self.assertTrue((myData.getDataEntry('contexts', 3) ==
                         7 * np.ones((3))).all())

    def test_resolveEntryPath(self):
        manager = DataUtil.createTestManager()
        data = manager.createDataObject([10, 20, 30])

        self.assertTrue(['parameters'] == data._resolveEntryPath('parameters'))
        self.assertTrue(['contexts'] == data._resolveEntryPath('contexts'))
        self.assertTrue(['steps', 'states'] ==
                        data._resolveEntryPath('states'))
        self.assertTrue(['steps', 'subSteps', 'subActions'] ==
                        data._resolveEntryPath('subActions'))

        data.setDataEntry(['parameters'], [...], np.zeros((10, 5)))
        data.setDataEntry('parameters', [...], np.ones((10, 5)))
        self.assertTrue((data.getDataEntry(['parameters'], [...]) ==
                         np.ones((10, 5))).all())
        self.assertTrue((data.getDataEntry('parameters', [...]) ==
                         np.ones((10, 5))).all())

        data.setDataEntry(['steps', 'actions'], [0, ...], np.zeros((20, 2)))
        data.setDataEntry('actions', [0, ...], np.ones((20, 2)))
        self.assertTrue((data.getDataEntry(['steps', 'actions'], [0, ...]) ==
                         np.ones((20, 2))).all())
        self.assertTrue((data.getDataEntry('actions', [0, ...]) ==
                         np.ones((20, 2))).all())

        data.setDataEntry(['steps', 'subSteps', 'subStates'], [0, 0, ...],
                          np.zeros((30, 1)))
        data.setDataEntry('subStates', [0, 0, ...], np.ones((30, 1)))
        self.assertTrue((data.getDataEntry(['steps', 'subSteps', 'subStates'],
                                           [0, 0, ...]) == np.ones((30, 1))).all())
        self.assertTrue((data.getDataEntry('subStates', [0, 0, ...]) ==
                         np.ones((30, 1))).all())

    def test_getNumElements(self):
        manager = DataUtil.createTestManager()
        data = manager.createDataObject([3, 4, 5])

        self.assertEqual(data.getNumElements(), 3)
        self.assertEqual(data.getNumElements('states'), 12)
        self.assertEqual(data.getNumElements('subActions'), 60)
        self.assertEqual(data.getNumElements('contexts'), 3)

    def test_getNumElementsForIndex(self):
        manager = DataUtil.createTestManager()
        data = manager.createDataObject([3, 4, 5])

        self.assertEqual(data.getNumElementsForIndex(0), 3)
        self.assertEqual(data.getNumElementsForIndex(0, [...]), 3)
        self.assertEqual(data.getNumElementsForIndex(1), 12)
        self.assertEqual(data.getNumElementsForIndex(1, [...]), 12)
        self.assertEqual(data.getNumElementsForIndex(1, [..., ...]), 12)
        self.assertEqual(data.getNumElementsForIndex(1, [..., slice(0, 2)]), 6)
        self.assertEqual(data.getNumElementsForIndex(1, [slice(2, 3),
                                                         slice(0, 2)]), 2)
        self.assertEqual(data.getNumElementsForIndex(2), 60)
        self.assertEqual(
            data.getNumElementsForIndex(
                2, ...), 60)  # test implicit cast to array of second argument (deprecated)
        self.assertEqual(
            data.getNumElementsForIndex(
                2,
                [...]),
            60)  # this should be the standart way
        self.assertEqual(data.getNumElementsForIndex(2, [..., ...]), 60)
        self.assertEqual(data.getNumElementsForIndex(2, [..., ..., ...]), 60)
        self.assertEqual(data.getNumElementsForIndex(2, [..., ..., slice(0, 2)]), 24)
        self.assertEqual(data.getNumElementsForIndex(2, [..., slice(1, 4),
                                                         slice(0, 2)]), 18)
        self.assertEqual(data.getNumElementsForIndex(2, [slice(0, 1),
                                                         slice(2, 3), slice(0, 2)]), 2)

        dataManager = DataManager('episodes')
        subDataManager = DataManager('steps')
        dataManager.subDataManager = subDataManager
        dataManager.addDataEntry('parameters', 5)
        dataManager.addDataAlias('pAlias', [('parameters', ...)])
        dataManager.addDataEntry('contexts', 2)
        data = dataManager.createDataObject([3, 4, 5])

        self.assertEqual(data.getNumElementsForIndex(0), 3)
        self.assertEqual(data.getNumElementsForIndex(0, [...]), 3)
        self.assertEqual(data.getNumElementsForIndex(1), 12)
        self.assertEqual(data.getNumElementsForIndex(1, [...]), 12)
        self.assertEqual(data.getNumElementsForIndex(1, [..., ...]), 12)
        self.assertEqual(data.getNumElementsForIndex(1, [slice(2, 3)]), 4)

    def test_mergeDataBack(self):
        dataManager = DataManager("manager")
        subDataManager = DataManager("subDataManager")
        dataManager.subDataManager = subDataManager
        dataManager.addDataEntry("entry1", 2)
        subDataManager.addDataEntry("entry2", 3)

        data1 = dataManager.createDataObject([10, 10])
        data1.setDataEntry("entry1", ..., np.ones((10, 2)))
        data1.setDataEntry("entry2", ..., np.ones((100, 3)))

        data2 = dataManager.createDataObject([5, 5])
        data2.setDataEntry("entry1", ..., np.zeros((5, 2)))
        data2.setDataEntry("entry2", ..., np.zeros((25, 3)))

        data1.mergeData(data2, False)

        self.assertEqual(data1.getNumElements("entry1"), 15)
        self.assertEqual(len(data1.dataStructure["subDataManager"]), 15)
        self.assertTrue((data1.getDataEntry("entry1", ...) ==
                         np.vstack((np.ones((10, 2)), np.zeros((5, 2))))).all())

    def test_mergeDataFront(self):
        dataManager = DataManager("manager")
        subDataManager = DataManager("subDataManager")
        dataManager.subDataManager = subDataManager
        dataManager.addDataEntry("entry1", 2)
        subDataManager.addDataEntry("entry2", 3)

        data1 = dataManager.createDataObject([10, 10])
        data1.setDataEntry("entry1", ..., np.ones((10, 2)))
        data1.setDataEntry("entry2", ..., np.ones((100, 3)))

        data2 = dataManager.createDataObject([5, 5])
        data2.setDataEntry("entry1", ..., np.zeros((5, 2)))
        data2.setDataEntry("entry2", ..., np.zeros((25, 3)))

        data1.mergeData(data2, True)

        self.assertEqual(data1.getNumElements("entry1"), 15)
        self.assertEqual(len(data1.dataStructure["subDataManager"]), 15)
        self.assertTrue((data1.getDataEntry("entry1", ...) ==
                         np.vstack((np.zeros((5, 2)), np.ones((10, 2))))).all())

    def test_mergeDataFrontNoSubmanager(self):
        dataManager = DataManager("manager")
        dataManager.addDataEntry("entry1", 2)

        data1 = dataManager.createDataObject([10, 10])
        data1.setDataEntry("entry1", ..., np.ones((10, 2)))

        data2 = dataManager.createDataObject([5, 5])
        data2.setDataEntry("entry1", ..., np.zeros((5, 2)))

        data1.mergeData(data2, True)

        self.assertEqual(data1.getNumElements("entry1"), 15)
        self.assertTrue((data1.getDataEntry("entry1", ...) ==
                         np.vstack((np.zeros((5, 2)), np.ones((10, 2))))).all())

    def test_nextAliases(self):
        dataManager = DataManager("manager", isTimeSeries=True)
        dataManager.addDataEntry("entry1", 1)
        dataManager.addDataEntry("entry2", 3)
        dataManager.addDataAlias("entries", [('entry1', ...), ('entry2', ...)])

        data1 = dataManager.createDataObject([10])
        dataMat = np.array(range(0,11))
        dataMat.resize(11,1)

        dataMatNext = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        dataMatLast = np.array([0, 0, 1, 2, 3, 4, 5, 6, 7, 8])
        dataMatNext.resize(10,1)
        dataMatLast.resize(10,1)

        data1.setDataEntry("allEntry1", ..., dataMat)

        nextEntry1 = data1.getDataEntry("nextEntry1", ...)
        allDataEntry1 = data1.getDataEntry("allEntry1", ...)
        lastEntry1 = data1.getDataEntry("lastEntry1", ...)

        self.assertTrue((nextEntry1 == dataMatNext).all())
        self.assertTrue((allDataEntry1 == dataMat).all())
        self.assertTrue((lastEntry1 == dataMatLast).all())

        allDataEntries = data1.getDataEntry('allEntries', slice(0,3))
        allDataEntriesMat = np.array([[0, 0, 0, 0], [1, 0, 0, 0], [2, 0, 0, 0]])
        self.assertTrue((allDataEntries == allDataEntriesMat).all())

    def test_PeriodicEntry(self):
        dataManager = DataManager("manager", isTimeSeries=False)
        dataManager.addDataEntry("entry1", 1)
        dataManager.addDataEntry("entry2", 3, isPeriodic=[True, False, True])
        dataManager.addDataAlias("entries", [('entry1',...), ('entry2', ...)])

        periodTest = dataManager.getPeriodicity('entries')
        self.assertTrue( periodTest == [False, True, False, True])
        data = dataManager.createDataObject(2)
        data.setDataEntry('entries', ..., np.array([[0, 8, 0, 2], [0, 2, 0, -8]]))

        entryPeriodic = data.getDataEntry('entries_periodic')
        self.assertTrue(sum(sum(np.abs(entryPeriodic - np.array([[0, 1.71681469, 0, 2], [0, 2, 0, 4.56637061]])))) < 0.001)


    def test_restrictedEntry(self):
        dataManager = DataManager("manager", isTimeSeries=False)
        dataManager.addDataEntry("entry1", 1)
        dataManager.addDataEntry("entry2", 3, isPeriodic=[True, False, True])
        dataManager.addDataAlias("entries", [('entry1', ...), ('entry2', ...)])

        data = dataManager.createDataObject(2)
        data.setDataEntry('entries', ..., np.array([[0, 8, 0, 2], [0, 2, 0, -8]]))

        entryRestricted = data.getDataEntry('entries_restricted')
        self.assertTrue(sum(sum(np.abs(entryRestricted - np.array([[0, 1, 0, 1], [0, 1, 0, -1]])))) < 0.001)

    def test_getSubDataStructure(self):
        dataManager = DataUtil.createTestManager()
        data = dataManager.createDataObject([10, 20, 30])

        subData1 = data.dataStructure.getSubdataStructures(...)
        subData2 = data.dataStructure.getSubdataStructures([slice(0,5),...])
        self.assertRaises(ValueError, data.dataStructure.getSubdataStructures, [..., 10, ...])

        self.assertEqual(len(subData1), 10)
        self.assertEqual(len(subData2), 100)


    def test_getReserveStorage(self):
        dataManager = DataUtil.createTestManager()
        data = dataManager.createDataObject([10, 20, 30])

        self.assertEqual(data.getNumElementsForDepth(2), 6000)

        data.reserveStorage([5, 10, 10])
        self.assertEqual(data.getNumElementsForDepth(2), 500)

        data.reserveStorage([20, 30], ...)
        self.assertEqual(data.getNumElementsForDepth(2), 3000)


        data.reserveStorage([50], [1, 2])
        self.assertEqual(data.getNumElementsForDepth(2), 3000 + 20)

    def testDataFromSettings(self):
        dataManager = DataUtil.createTestManager()
        dataManager.addOptionalDataEntry('optionalEntry', False, 2, np.array([[-1, -1]]), np.array([[5, 5]]))

        data = dataManager.createDataObject([10, 20, 30])
        dataManager.settings.setProperty('optionalEntry', np.array([[-2, -2]]))
        optionalEntry = data.getDataEntry('optionalEntry')
        optionalEntryTrue = np.tile(np.array([[-2, -2]]), (10,1))
        self.assertTrue((optionalEntryTrue == optionalEntry).all() )

    def testNativeAccess(self):
        dataManager = DataUtil.createTestManager()

        data = dataManager.createDataObject([10, 20, 30])

        data.dataManager
        dummy = data[1].states

        data[2].states = dummy + 1


        self.assertTrue((data[2].states == dummy + 1).all())

if __name__ == '__main__':
    unittest.main()
