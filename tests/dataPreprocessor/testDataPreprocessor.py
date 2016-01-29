import unittest
import sys
import numpy as np
import math

# FIXME we should find a better ways than jsut including all the paths:
# e.g. import from ToolBox.Data, ToolBox.Interfaces
sys.path.append('../../src/')

sys.path.append('../')


from data.DataAlias import DataAlias
from data.DataEntry import DataEntry
from data.DataManager import DataManager

import DataUtil

from dataPreprocessor.DataPreprocessor import DataPreprocessor


class testDataPreprocessor(unittest.TestCase):

    def test_init_givenNoName_expectNoException(self):
        datapreprocessor = DataPreprocessor()
        
        self.assertIsInstance(datapreprocessor, DataPreprocessor)
        self.assertEqual(datapreprocessor.name, "DataPreprocessor")
        self.assertEqual(datapreprocessor.iteration, 0)

    def test_init_givenName_expectNoException(self):
        datapreprocessor = DataPreprocessor("TestName")
        
        self.assertIsInstance(datapreprocessor, DataPreprocessor)
        self.assertEqual(datapreprocessor.name, "TestName")
        self.assertEqual(datapreprocessor.iteration, 0)
        
    def test_init_givenEmptyName_expectRuntimeError(
            self):
        self.assertRaises(
            RuntimeError, lambda: DataPreprocessor(""))

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
