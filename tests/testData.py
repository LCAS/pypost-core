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

        dataObject = dataManager.getDataObject([10, 5, 3])

        self.assertEqual(dataObject.getDataEntry(['parameters']).shape[0], 10)

        self.assertEqual(
            dataObject.getDataEntry(['parameters'], [...]).shape[0], 10)

        self.assertEqual(
            dataObject.getDataEntry(['parameters'], [1]).shape[0], 1)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'states'], [1]).shape[0], 5)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'states'], [3]).shape[0], 5)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'states'],
                                    [..., 1]).shape[0], 10)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'states'],
                                    [..., ...]).shape[0], 50)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'states']).shape[0], 50)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'subSteps', 'subActions'],
                                    [..., ..., ...]).shape[0], 150)

        self.assertEqual(
            dataObject.getDataEntry(
                ['steps', 'subSteps', 'subActions']).shape[0], 150)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'subSteps', 'subActions'],
                                    [..., ..., 1]).shape[0], 50)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'subSteps', 'subActions'],
                                    [..., 1, ...]).shape[0], 30)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'subSteps', 'subActions'],
                                    [..., 1]).shape[0], 30)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'subSteps', 'subActions'],
                                    [..., 1, 1]).shape[0], 10)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'subSteps', 'subActions'],
                                    [1, ..., ...]).shape[0], 15)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'subSteps', 'subActions'],
                                    [1]).shape[0], 15)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'subSteps', 'subActions'],
                                    1).shape[0], 15)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'subSteps', 'subActions'],
                                    [1, ..., 1]).shape[0], 5)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'subSteps', 'subActions'],
                                    [1, 1, ...]).shape[0], 3)

        self.assertEqual(
            dataObject.getDataEntry(['steps', 'subSteps', 'subActions'],
                                    [1, 1, 1]).shape[0], 1)

if __name__ == '__main__':
    unittest.main()
