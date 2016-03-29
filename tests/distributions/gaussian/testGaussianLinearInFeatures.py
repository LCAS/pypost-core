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

        self.assertEqual(self.getNumParameters(), 30)

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
