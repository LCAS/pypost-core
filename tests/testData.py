import unittest
import sys
import numpy as np
sys.path.append('../src/data')
from DataEntry import DataEntry
from DataManager import DataManager


class testDataManager(unittest.TestCase):

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

        myData = dataManager.getDataObject([10, 5, 3])

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
        dataManager.addDataEntry('parameters', 5)
        myData = dataManager.getDataObject([10, 5, 3])

        # set the data for the parameters of all episodes
        myData.setDataEntry(['parameters'], [...], [1, 2, 3, 4, 5])

        # the first episode should have different parameters
        myData.setDataEntry(['parameters'], [0], [1, 1, 1, 1, 1])

        self.assertTrue((myData.dataStructure['parameters'][0] ==
                         np.array([1, 1, 1, 1, 1])).all())
        self.assertTrue((myData.dataStructure['parameters'][1] ==
                         np.array([1, 2, 3, 4, 5])).all())
        self.assertTrue((myData.dataStructure['parameters'][9] ==
                         np.array([1, 2, 3, 4, 5])).all())

        # this should not change anything
        myData.setDataEntry(['parameters'], [], np.array([1, 2, 3, 4, 5]))
        myData.setDataEntry(['parameters'], [0], np.array([1, 1, 1, 1, 1]))

        self.assertTrue((myData.dataStructure['parameters'][0] ==
                         np.array([1, 1, 1, 1, 1])).all())
        self.assertTrue((myData.dataStructure['parameters'][1] ==
                         np.array([1, 2, 3, 4, 5])).all())
        self.assertTrue((myData.dataStructure['parameters'][9] ==
                         np.array([1, 2, 3, 4, 5])).all())

        # tests for getDataEntry
        self.assertTrue((myData.getDataEntry('parameters') ==
                         myData.dataStructure['parameters']).all())

        self.assertTrue((myData.getDataEntry('parameters', ...) ==
                         myData.dataStructure['parameters']).all())

        self.assertTrue((myData.getDataEntry('parameters')[4] ==
                         myData.dataStructure['parameters'][4]).all())

        self.assertTrue((myData.getDataEntry('parameters', [4]) ==
                         myData.dataStructure['parameters'][4]).all())

    def test_setgetDataEntryLocalLayer(self):
        dataManager = DataManager('episodes')
        subDataManager = DataManager('steps')
        subSubDataManager = DataManager('subSteps')

        dataManager.subDataManager = subDataManager
        subDataManager.subDataManager = subSubDataManager

        subSubDataManager.addDataEntry('subActions', 2)

        myData = dataManager.getDataObject([10, 5, 3])

        # set the data for all subActions of all episodes, steps and subSteps
        myData.setDataEntry(['steps', 'subSteps', 'subActions'],
                            [], np.ones(300).reshape(150, 2))

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

if __name__ == '__main__':
    unittest.main()
