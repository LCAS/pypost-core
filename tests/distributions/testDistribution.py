import unittest
import numpy as np
import math
from data.DataManager import DataManager

import DataUtil

from distributions.Distribution import Distribution


class testDistribution(unittest.TestCase):

    def test_init_expectNoException(self):
        dataManager = DataManager("TestDataManager")
        distribution = Distribution(dataManager)

        self.assertIsInstance(distribution, Distribution)
        self.assertEqual(distribution.dataManager, dataManager)

    def test_setDataProbabilityEntries_givenNames_expectPropabilityEntry(self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 1)
        dataManager.addDataEntry("In", 1)
        dataManager.addDataEntry("In2", 1)
        distribution = Distribution(dataManager)

        distribution.setOutputVariables(["Out"])
        distribution.setInputVariables(["In", "In2"])

        distribution.setDataProbabilityEntries()

        self.assertEqual(distribution.getDataProbabilityNames(), ["logQOii"])

    def test_registerProbabilityNames_givenNames_expectRegisteredFunction(
            self):
        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 1)
        dataManager.addDataEntry("In", 1)
        dataManager.addDataEntry("In2", 1)
        distribution = Distribution(dataManager)

        distribution.setOutputVariables(["Out"])
        distribution.setInputVariables(["In", "In2"])
        distribution.setDataProbabilityEntries()

        distribution.registerProbabilityNames("testLayer")

    def test_sampleFromDistribution_NotImplementedError(self):
        dataManager = DataManager("TestDataManager")
        distribution = Distribution(dataManager)

        self.assertRaises(NotImplementedError,
                          distribution.sampleFromDistribution, 1)

    def test_getDataProbabilities_NotImplementedError(self):
        dataManager = DataManager("TestDataManager")
        distribution = Distribution(dataManager)

        self.assertRaises(NotImplementedError,
                          distribution.getDataProbabilities, [], [])

if __name__ == '__main__':
    unittest.main()
