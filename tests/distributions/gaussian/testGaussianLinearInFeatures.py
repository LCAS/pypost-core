import unittest
import numpy as np
import math
from data.DataManager import DataManager

import DataUtil

from distributions.gaussian.GaussianLinearInFeatures import GaussianLinearInFeatures


class testGaussianLinearInFeatures(unittest.TestCase):

    def test_init_expectNoException(self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 3)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            "Out",
            ["In"],
            "MY_TEST_FUNCTION_NAME",
            None,
            True)
        glf.setDataProbabilityEntries()
        glf.registerProbabilityNames("testLayer")

        self.assertIsInstance(glf, GaussianLinearInFeatures)

    def test_getNumParameters_givenParameters_expectCorrectNumberOfOutputParameters(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 3)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            "Out",
            ["In"],
            "MY_TEST_FUNCTION_NAME",
            None,
            True)
        glf.setDataProbabilityEntries()
        glf.registerProbabilityNames("testLayer")

        self.assertEqual(glf.getNumParameters(), 18)

    def test_getMean_givenParameters_expectCorrectMean(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 3)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            "Out",
            ["In"],
            "MY_TEST_FUNCTION_NAME",
            None,
            True)
        glf.setDataProbabilityEntries()
        glf.registerProbabilityNames("testLayer")

        self.assertTrue(
            np.allclose(glf.getMean(), np.transpose(np.array([[0.0, 0.0, 0.0]])), 1e-05, 0.01))

    def test_getCov_setCov_givenCovNoSave_expectGivenCov(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 3)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            "Out",
            ["In"],
            "MY_TEST_FUNCTION_NAME",
            None,
            True)
        glf.setDataProbabilityEntries()
        glf.registerProbabilityNames("testLayer")

        glf.saveCovariance = False
        glf.setCovariance(4 * np.identity(2))
        self.assertTrue(np.allclose(glf.getCovariance(), 4 * np.identity(2)))

    def test_getCov_setCov_givenCovSave_expectGivenCov(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 3)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            "Out",
            ["In"],
            "MY_TEST_FUNCTION_NAME",
            None,
            True)
        glf.setDataProbabilityEntries()
        glf.registerProbabilityNames("testLayer")

        glf.saveCovariance = True
        glf.setCovariance(4 * np.identity(2))
        self.assertTrue(np.allclose(glf.getCovariance(), 4 * np.identity(2)))

    def test_getSigma_setSigma_givenSigmaNoSave_expectGivenSigma(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 3)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            "Out",
            ["In"],
            "MY_TEST_FUNCTION_NAME",
            None,
            True)
        glf.setDataProbabilityEntries()
        glf.registerProbabilityNames("testLayer")

        glf.saveCovariance = False
        glf.setSigma(4 * np.identity(2))
        self.assertTrue(np.allclose(glf.getSigma(), 4 * np.identity(2)))

    def test_getSigma_setSigma_givenSigmaSave_expectGivenSigma(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 3)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            "Out",
            ["In"],
            "MY_TEST_FUNCTION_NAME",
            None,
            True)
        glf.setDataProbabilityEntries()
        glf.registerProbabilityNames("testLayer")

        glf.saveCovariance = True
        glf.setSigma(4 * np.identity(2))
        self.assertTrue(np.allclose(glf.getSigma(), 4 * np.identity(2)))

    '''
    def test_getExpectationAndSigma_NotImplementedError(self):
        dataManager = DataManager("TestDataManager")
        distribution = DistributionWithMeanAndVariance(dataManager)

        self.assertRaises(NotImplementedError,
                          distribution.getExpectationAndSigma, 1, [])

    def test__registerMappingInterfaceDistribution_givenRegisterFlag_ExpectNoError(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 3)
        dataManager.addDataEntry("In", 3)
        distribution = DistributionWithMeanAndVariance(dataManager)
        distribution.setOutputVariables(["Out"])
        distribution.setInputVariables(["In"])
        distribution.setDataProbabilityEntries()
        distribution.registerProbabilityNames("testLayer")

        distribution.registerDataFunctions = True
        distribution._registerMappingInterfaceDistribution()

    def test__registerMappingInterfaceDistribution_givenNoRegisterFlag_ExpectNoError(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 3)
        dataManager.addDataEntry("In", 3)
        distribution = DistributionWithMeanAndVariance(dataManager)
        distribution.setOutputVariables(["Out"])
        distribution.setInputVariables(["In"])
        distribution.setDataProbabilityEntries()
        distribution.registerProbabilityNames("testLayer")

        distribution.registerDataFunctions = False
        distribution._registerMappingInterfaceDistribution()
    '''

if __name__ == '__main__':
    unittest.main()
