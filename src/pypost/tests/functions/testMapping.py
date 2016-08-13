import unittest
import numpy as np
import math

from pypost.data.DataAlias import DataAlias
from pypost.data.DataEntry import DataEntry
from pypost.data.DataManager import DataManager
from pypost.tests import DataUtil


from pypost.functions.Mapping import Mapping


class testMapping(unittest.TestCase):

    def test_init_givenNoInputNoOutputNoName_expectNoException(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)

        mapping = Mapping(dataManager)

        self.assertIsInstance(mapping, Mapping)

    def test_init_givenSingleInputSingleOutputNoName_expectNoException(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)

        mapping = Mapping(dataManager, ['X'], ['Y'], "TestMapping")

        self.assertIsInstance(mapping, Mapping)
        self.assertEqual(mapping.name, 'TestMapping')

    def test_init_givenSingleInputMultipleOutputNoName_expectRuntimeError(
            self):
        # note that this test may start failing if multiple output variables
        # are getting allowed
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)

        self.assertRaises(
            ValueError, lambda: Mapping(
                dataManager, [
                    'Y', 'Z'], ['X'], "TestMapping"))


    def test_setInputVariables_givenIntputvariablesString_expectDeprecationWarning(
            self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)

        mapping = Mapping(dataManager, ['X'], ['Y'], "TestMapping")

        self.assertRaises(DeprecationWarning,
                          mapping.setInputVariables, 'var1')


    def test_getInputVariables_given_expectInputVariablesGivenToConstructor(
            self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)

        mapping = Mapping(dataManager, ['X'], ['Y'], "TestMapping")

        self.assertEqual(mapping.getInputVariables(), ['X'])

    def test_setInputVariables_givenInputVariablesNoAppend_expectOnlySetInputVariables(
            self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)
        dataManager.addDataEntry('A', 1)
        dataManager.addDataEntry('B', 1)

        mapping = Mapping(dataManager, ['X'], ['Y'], "TestMapping")

        mapping.setInputVariables(['A', 'B'], None, False)

        self.assertEqual(mapping.getInputVariables(), ['A', 'B'])

    def test_setInputVariables_givenInputVariablesAppend_expectConstructorAndSetInputVariables(
            self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)
        dataManager.addDataEntry('A', 1)
        dataManager.addDataEntry('B', 1)

        mapping = Mapping(dataManager, ['X'], ['Y'], "TestMapping")

        mapping.setInputVariables(['A', 'B'], None, True)

        self.assertEqual(mapping.getInputVariables(), ['X', 'A', 'B'])

    def test_setInputVariables_givenNumDim_expectNotSupportet(
            self):
        '''
        This test may fail if the functionality gets implemented
        '''
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)
        dataManager.addDataEntry('A', 1)
        dataManager.addDataEntry('B', 1)

        mapping = Mapping(dataManager, ['X'], ['Y'], "TestMapping")

        self.assertRaises(
            NotImplementedError, lambda: mapping.setInputVariables(['A', 'B'], 5))

    def test_setInputVariables_givenNumberInInputvariables_expectNotSupportet(
            self):
        '''
        This test may fail if the functionality gets implemented
        '''
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)
        dataManager.addDataEntry('A', 1)
        dataManager.addDataEntry('B', 1)

        mapping = Mapping(dataManager, ['X'], ['Y'], "TestMapping")

        self.assertRaises(
            DeprecationWarning, lambda: mapping.setInputVariables([5, 'A', 'B'], None, True))

    def test_getOutputVariables_given_expectOutputVariablesGivenToConstructor(
            self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)

        mapping = Mapping(dataManager, ['X'], ['Y'], "TestMapping")

        self.assertEqual(mapping.getOutputVariables(), ['Y'])

    def test_setOutputVariables_givenSingleOutputVariable_expectSetOutputVariables(
            self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)
        dataManager.addDataEntry('A', 1)

        mapping = Mapping(dataManager, ['X'], ['Y'], "TestMapping")

        mapping.setOutputVariables(['A'])

        self.assertEqual(mapping.getOutputVariables(), ['A'])

    def test_setOutputVariables_givenMultipleOutputVariables_expectRuntimeError(
            self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)

        mapping = Mapping(dataManager, ['X'], ['Y'], "TestMapping")

        self.assertRaises(
            ValueError, lambda: mapping.setOutputVariables(['A', 'B']))

    def test_setOutputDimension(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)

        mapping = Mapping(dataManager, ['X'], ['Y'], "TestMapping")

        mapping.setOutputDimension(4324)

        self.assertEqual(4324, mapping.dimOutput)
        self.assertEqual([], mapping.outputVariables)

if __name__ == '__main__':
    unittest.main()
