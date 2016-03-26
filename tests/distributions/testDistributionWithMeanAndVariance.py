import unittest
import numpy as np
import math
from data.DataManager import DataManager

import DataUtil

from distributions.DistributionWithMeanAndVariance import DistributionWithMeanAndVariance


class testDistribution(unittest.TestCase):

    def test_init_expectNoException(self):
        dataManager = DataManager("TestDataManager")
        distribution = DistributionWithMeanAndVariance(dataManager)

        self.assertIsInstance(distribution, DistributionWithMeanAndVariance)
        self.assertEqual(distribution.dataManager, dataManager)

    def test_sampleFromDistribution_givenSingleExpAndSigma_SamplesFromDistribution(
            self):
        class DistributionWithMeanAndVarianceTest:

            def getExpectationAndSigma(self, numElements, inputData, *args):
                return (np.array([[[5]]]), np.array([[[0.1]]]))

        dataManager = DataManager("TestDataManager")
        distribution = DistributionWithMeanAndVariance(dataManager)

        samples = distribution.sampleFromDistribution(1)
        self.assertTrue(4.9 <= samples[0][0][0] <= 5.1)

    def test_sampleFromDistribution_givenSingleExpAndSigma_SamplesFromDistribution(
            self):
        class DistributionWithMeanAndVarianceTest:

            def getExpectationAndSigma(self, numElements, inputData, *args):
                return (
                    np.array([[[5], [6], [7]]]), np.array([[[0.1], [0.1], [0.1]]]))

        dataManager = DataManager("TestDataManager")
        distribution = DistributionWithMeanAndVariance(dataManager)

        samples = distribution.sampleFromDistribution(1)
        self.assertTrue(4.9 <= samples[0][0][0] <= 5.1)

    def test_setDataProbabilityEntries_givenNames_expectPropabilityEntry(self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 1)
        dataManager.addDataEntry("In", 1)
        dataManager.addDataEntry("In2", 1)
        distribution = DistributionWithMeanAndVariance(dataManager)

        distribution.setOutputVariables(["Out"])
        distribution.setInputVariables(["In", "In2"])

        distribution.setDataProbabilityEntries()

        self.assertEqual(distribution.getDataProbabilityNames(), ["logQOii"])

    def test_getExpectationAndSigma_NotImplementedError(self):
        dataManager = DataManager("TestDataManager")
        distribution = DistributionWithMeanAndVariance(dataManager)

        self.assertRaises(NotImplementedError,
                          distribution.getExpectationAndSigma, 1, [])

if __name__ == '__main__':
    unittest.main()
