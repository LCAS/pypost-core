import unittest

import numpy as np

from pypost.data.DataManager import DataManager
from pypost.distributions.GaussianLinearInFeatures import GaussianLinearInFeatures


class testGaussianLinearInFeatures(unittest.TestCase):

    def test_init_expectNoException(self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 2)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            ["In"],"Out",
            "MY_TEST_FUNCTION_NAME",
            None,
            True)


        self.assertIsInstance(glf, GaussianLinearInFeatures)


    def test_getMean_givenParameters_expectCorrectMean(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 2)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            ["In"],
            "Out",
            "MY_TEST_FUNCTION_NAME",
            None,
            True)

        self.assertTrue(
            np.allclose(glf.getMean(), np.transpose(np.array([[0.0, 0.0]])), 1e-05, 0.01))

    def test_getCov_setCov_givenCovNoSave_expectGivenCov(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 2)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            ["In"],
            "Out",
            "MY_TEST_FUNCTION_NAME",
            None,
            True)

        glf.saveCovariance = False
        glf.setCovariance(4 * np.identity(2))
        self.assertTrue(np.allclose(glf.getCovariance(), 4 * np.identity(2)))

    def test_getCov_setCov_givenCovSave_expectGivenCov(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 2)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            ["In"],
            "Out",
            "MY_TEST_FUNCTION_NAME",
            None,
            True)

        glf.saveCovariance = True
        glf.setCovariance(4 * np.identity(2))
        self.assertTrue(np.allclose(glf.getCovariance(), 4 * np.identity(2)))

    def test_getSigma_setSigma_givenSigmaNoSave_expectGivenSigma(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 2)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            ["In"],
            "Out",
            "MY_TEST_FUNCTION_NAME",
            None,
            True)

        glf.saveCovariance = False
        glf.setSigma(4 * np.identity(2))
        self.assertTrue(np.allclose(glf.getSigma(), 4 * np.identity(2)))

    def test_getSigma_setSigma_givenSigmaSave_expectGivenSigma(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 2)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            ["In"],
            "Out",
            "MY_TEST_FUNCTION_NAME",
            None,
            True)

        glf.saveCovariance = True
        glf.setSigma(4 * np.identity(2))
        self.assertTrue(np.allclose(glf.getSigma(), 4 * np.identity(2)))

    def test_callFunction(self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 2)
        dataManager.addDataEntry("In", 3)
        glf = GaussianLinearInFeatures(
            dataManager,
            [],
            "Out",
            "MY_TEST_FUNCTION_NAME",
            None,
            True)

        glf.saveCovariance = True
        glf.setSigma(4 * np.identity(2))

        samples = glf(100000, fromData = False)
        self.assertTrue(sum(sum(abs(np.cov(samples.transpose()) - glf.getCovariance()))) < 1.0 )
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
