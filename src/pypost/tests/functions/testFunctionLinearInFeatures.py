import unittest
import numpy as np
from pypost.data.DataManager import DataManager
from pypost.functions.Function import Function
from pypost.functions.FunctionLinearInFeatures import FunctionLinearInFeatures


class testFunctionLinearInFeatures(unittest.TestCase):
    def test_init(self):
        self.assertRaises(ValueError, FunctionLinearInFeatures,
                          None, [], None, None, None)


        self.assertRaises(ValueError, FunctionLinearInFeatures,
                          None, None, None, None, [])

        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)
        f = FunctionLinearInFeatures(dataManager, ['X'], ['Y'], None, None, False)
        self.assertEqual(None, f.bias)

    def test_getExpectation(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 2)
        dataManager.addDataEntry('Y', 1)
        f = FunctionLinearInFeatures(dataManager, ['X'], ['Y'], None, None)

        X = np.array([[1, 1],[2,1]])
        f.bias = np.ones((1)) * 5
        f.weights = np.array([[2, 1],])
        Y = f.bias + np.dot(X, f.weights.transpose())

        self.assertTrue((Y == f.computeOutput(inputFeatures=X)).all())

        self.assertTrue((Y == f(X, fromData = False)).all())

        data = dataManager.getDataObject(2)
        data.setDataEntry('X',..., X)

        self.assertTrue((Y == f(data)).all())

    def test_setWeightsAndBias(self):
        dataManager = DataManager('values')
        dataManager.addDataEntry('X', 1)
        dataManager.addDataEntry('Y', 1)
        f = FunctionLinearInFeatures(dataManager, ['X'], ['Y'], None, None)

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

