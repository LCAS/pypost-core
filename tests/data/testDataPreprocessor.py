import unittest
import numpy as np
import math
from data.DataAlias import DataAlias
from data.DataEntry import DataEntry
from data.DataManager import DataManager
from data.DataCollection import DataCollection

import DataUtil

from data.DataPreprocessor import DataPreprocessor


class testDataPreprocessor(unittest.TestCase):

    def test_init_givenNoName_expectNoException(self):
        datapreprocessor = DataPreprocessor()

        self.assertIsInstance(datapreprocessor, DataPreprocessor)
        self.assertEqual(datapreprocessor.name, 'data')
        self.assertEqual(datapreprocessor.iteration, 0)

    def test_init_givenName_expectNoException(self):
        datapreprocessor = DataPreprocessor("TestName")

        self.assertIsInstance(datapreprocessor, DataPreprocessor)
        self.assertEqual(datapreprocessor.name, "TestName")
        self.assertEqual(datapreprocessor.iteration, 0)

    def test_init_givenEmptyName_expectRuntimeError(self):
        self.assertRaises(ValueError, DataPreprocessor, "")

    def test_preprocessData_NotImplementedError(self):
        datapreprocessor = DataPreprocessor("TestName")
        self.assertRaises(NotImplementedError,
                          datapreprocessor.preprocessData, 1)

    def test_preprocessDataCollection_NotImplementedError(self):
        datapreprocessor = DataPreprocessor("TestName")
        dataCollection = DataCollection()
        self.assertRaises(NotImplementedError,
                          datapreprocessor.preprocessDataCollection,
                          dataCollection)

    def test_preprocessDataCollection_givenTrueOverwrittenPreprocessFunc_expectFalse(
            self):
        # we are overwriting the preprocessData function to get code coverage
        # for the case of an child class implementing this method
        class DataPreprocessorOverwrite(DataPreprocessor):

            def preprocessData(self, data):
                return not data

        datapreprocessor = DataPreprocessorOverwrite("TestName")
        dataCollection = DataCollection()
        dataCollection.setStandardData(True)

        datapreprocessor.preprocessDataCollection(dataCollection)
        self.assertEqual(dataCollection.getDataObject('TestName'), False)

    def test_setIteration_givenPositiveIterationValue_expectGivenInputVariable(
            self):
        datapreprocessor = DataPreprocessor()
        datapreprocessor.setIteration(5)

        self.assertEqual(datapreprocessor.iteration, 5)

    def test_addMappingFunction_givenNegativeIterationValue_expectRuntimeError(
            self):
        datapreprocessor = DataPreprocessor()
        self.assertRaises(
            RuntimeError, lambda: datapreprocessor.setIteration(-5))

if __name__ == '__main__':
    unittest.main()
