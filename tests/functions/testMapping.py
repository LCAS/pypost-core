import unittest
import numpy as np
import math

from data.DataAlias import DataAlias
from data.DataEntry import DataEntry
from data.DataManager import DataManager

import DataUtil

from functions.Mapping import Mapping


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
            RuntimeError, lambda: Mapping(
                dataManager, ['X'], [
                    'Y', 'Z'], "TestMapping"))

    def test_getsetInputVariables_givenAdditionalIntputvariables_expectGivenInputVariables(
            self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)

        mapping = Mapping(dataManager, ['X'], ['Y'], "TestMapping")

        mapping.setAdditionalInputVariables(['W', 'Z'])

        self.assertEqual(mapping.getAdditionalInputVariables(), ['W', 'Z'])

    def test_addMappingFunction_givenOneToOneMappingFromMinusToPlusPi_expectSinAndSinGradientOutput(
            self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 11, -100, 100)
        dataManager.addDataEntry('Y', 11)
        dataManager.finalize()

        data = dataManager.getDataObject(1)

        # functions to map
        valueFunction = lambda numElements, X: np.sin(X)
        gradientFunction = lambda numElements, X: np.cos(X)

        mapping = Mapping(dataManager, ['X'], ['Y'], 'TestMapping')
        mapping.addMappingFunction(
            valueFunction,
            None,
            'valueFunction')
        mapping.addMappingFunction(
            gradientFunction,
            [],
            'gradientFunction')

        data.setDataEntry(
            'X', [], np.array([np.linspace(-np.pi, np.pi, 11)]))

        mapping.callDataFunction('valueFunction', data, [])

        Y = data.getDataEntry('Y')
        dY = mapping.callDataFunctionOutput(
            'gradientFunction',
            data, [])

        np.testing.assert_almost_equal(Y,
                                       [[
                                           0, -0.587785252,
                                           -0.951056516, -0.951056516,
                                           -0.587785252, 0,
                                           0.587785252, 0.951056516,
                                           0.951056516, 0.587785252,
                                           0
                                       ]])
        np.testing.assert_almost_equal(dY[0][0],
                                       [[
                                           -1, -0.80901699,
                                           -0.30901699, 0.30901699,
                                           0.80901699, 1,
                                           0.80901699, 0.30901699,
                                           -0.30901699, -0.80901699,
                                           -1
                                       ]])

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
            RuntimeError, lambda: mapping.setOutputVariables(['A', 'B']))

if __name__ == '__main__':
    unittest.main()
