import unittest
import numpy as np
from rlt.data.DataManager import DataManager
from rlt.functions.Function import Function
from rlt.functions.FunctionLinearInFeatures import FunctionLinearInFeatures
from rlt.parametricModels.ParametricFunction import ParametricFunction
from rlt.learner.parameterOptimization.HyperParameterObject \
import HyperParameterObject


class testFunctionLinearInFeatures(unittest.TestCase):
    def test_init(self):
        self.assertRaises(ValueError, FunctionLinearInFeatures,
                          None, [], None, None, None)


        self.assertRaises(ValueError, FunctionLinearInFeatures,
                          None, None, None, None, [])

        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)
        f = FunctionLinearInFeatures(dataManager, 'X', ['Y'], None, None, False)
        self.assertEqual(None, f.bias)

    def test_getExpectation(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)
        f = FunctionLinearInFeatures(dataManager, 'X', ['Y'], None, None)

        f.bias = np.zeros((10))
        expect = np.tile(f.bias[np.newaxis, :].T, (10, 1))
        self.assertTrue((expect == f.getExpectation(10)).all())

        f = FunctionLinearInFeatures(dataManager, 'X', ['Y'], None, None)

        f.bias = np.zeros((10, 10))
        expect = np.tile(f.bias.conj().T, (10, 1))
        self.assertTrue((expect == f.getExpectation(10)).all())

        f.weights = np.zeros((0))

        self.assertRaises(ValueError, f.getExpectation, 10)

        inputFeatures = np.ones((10))*2
        f.weights = np.ones((10, 10))*3

        expect += inputFeatures.dot(f.weights.conj().T)

        self.assertTrue((expect == f.getExpectation(10, inputFeatures)).all())

    def test_setWeightsAndBias(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)
        f = FunctionLinearInFeatures(dataManager, 'X', ['Y'], None, None)

        f.dimOutput = 10
        f.dimInput = 15
        bias = np.ones((10))
        weights = np.ones((10, 15))*3

        f.setWeightsAndBias(weights, bias)

        self.assertTrue((bias == f.bias).all())
        self.assertTrue((weights == f.weights).all())

        bias2 = np.ones((5))
        weights2 = np.ones((0))*3
        self.assertRaises(ValueError, f.setWeightsAndBias, bias2, weights)
        self.assertRaises(ValueError, f.setWeightsAndBias, bias, weights2)
        self.assertRaises(ValueError, f.setWeightsAndBias, bias2, weights2)

    def test_getNumParameters(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 5)
        dataManager.addDataEntry('Y', 5)
        f = FunctionLinearInFeatures(dataManager, 'X', ['Y'], None, None)

        self.assertEqual(30, f.getNumParameters())

    def test_getGradient(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 5)
        dataManager.addDataEntry('Y', 5)
        inputMatrix = np.ones((2, 3))
        f = FunctionLinearInFeatures(dataManager, 'X', ['Y'], None, None)

        expect = np.hstack((np.ones((inputMatrix.shape[0], 5)),
                            np.tile(inputMatrix, (1, 5))));
        self.assertTrue((expect == f.getGradient(inputMatrix)).all())

    def test_setgetParameterVector(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 5)
        dataManager.addDataEntry('Y', 5)
        f = FunctionLinearInFeatures(dataManager, 'X', ['Y'], None, None)
        theta = np.ones((6, 5))*2

        f.setParameterVector(theta)
        self.assertTrue((f.bias == theta[0, :]).all())
        self.assertTrue((f.weights == theta[1:]).all())

        self.assertTrue((theta == f.getParameterVector()).all())
