import unittest
import numpy as np
import math
from data.DataManager import DataManager

import DataUtil

from distributions.DistributionWithMeanAndVariance import DistributionWithMeanAndVariance


class testDistributionWithMeanAndVariance(unittest.TestCase):

    def test_init_expectNoException(self):
        dataManager = DataManager("TestDataManager")
        distribution = DistributionWithMeanAndVariance(dataManager)

        self.assertIsInstance(distribution, DistributionWithMeanAndVariance)
        self.assertEqual(distribution.dataManager, dataManager)

    def test_sampleFromDistribution_givenSingleExpAndSigma_SamplesFromDistribution(
            self):
        class DistributionWithMeanAndVarianceTest(
                DistributionWithMeanAndVariance):

            def DistributionWithMeanAndVarianceTest(self, dataManager):
                DistributionWithMeanAndVariance.__init__(self, dataManager)

            def getExpectationAndSigma(self, numElements, inputData, *args):
                return (np.array([[[5]]]), np.array([[[0.1]]]))

        dataManager = DataManager("TestDataManager")
        distribution = DistributionWithMeanAndVarianceTest(dataManager)

        samples = distribution.sampleFromDistribution(1, [])
        # test for 3-sigma env: 99.7% - can fail sometimes
        self.assertTrue(4.7 <= samples[0][0][0] <= 5.3)

    def test_sampleFromDistribution_givenEmptyExpAndMultiSigma_SamplesFromDistribution(
            self):
        class DistributionWithMeanAndVarianceTest(
                DistributionWithMeanAndVariance):

            def DistributionWithMeanAndVarianceTest(self, dataManager):
                DistributionWithMeanAndVariance.__init__(self, dataManager)

            def getExpectationAndSigma(self, numElements, inputData, *args):
                return (
                    np.zeros((1, 15, 15)), np.ones((1, 15, 15)))

        dataManager = DataManager("TestDataManager")
        distribution = DistributionWithMeanAndVarianceTest(dataManager)

        samples = distribution.sampleFromDistribution(1, [])
        # FIXME there are random numbers involved add asserts. for now we are
        # only testing correct execution

    def test_sampleFromDistribution_given2DExpAndMultiSigma_SamplesFromDistribution(
            self):
        class DistributionWithMeanAndVarianceTest(
                DistributionWithMeanAndVariance):

            def DistributionWithMeanAndVarianceTest(self, dataManager):
                DistributionWithMeanAndVariance.__init__(self, dataManager)

            def getExpectationAndSigma(self, numElements, inputData, *args):
                return (
                    np.zeros((1, 5, 2)), np.ones((1, 5, 2)))

        dataManager = DataManager("TestDataManager")
        distribution = DistributionWithMeanAndVarianceTest(dataManager)

        samples = distribution.sampleFromDistribution(1, [])
        # FIXME there are random numbers involved add asserts. for now we are
        # only testing correct execution

    def test_sampleFromDistribution_given3DExpAndMultiSigma_expectNotImplementedError(
            self):
        class DistributionWithMeanAndVarianceTest(
                DistributionWithMeanAndVariance):

            def DistributionWithMeanAndVarianceTest(self, dataManager):
                DistributionWithMeanAndVariance.__init__(self, dataManager)

            def getExpectationAndSigma(self, numElements, inputData, *args):
                return (
                    np.zeros((2, 5, 2)), np.ones((2, 5, 2)))

        dataManager = DataManager("TestDataManager")
        distribution = DistributionWithMeanAndVarianceTest(dataManager)

        self.assertRaises(
            NotImplementedError,
            distribution.sampleFromDistribution, 1, [])

    def test_sampleFromDistribution_given2DExpAnd3DSigma_expectNotImplementedError(
            self):
        class DistributionWithMeanAndVarianceTest(
                DistributionWithMeanAndVariance):

            def DistributionWithMeanAndVarianceTest(self, dataManager):
                DistributionWithMeanAndVariance.__init__(self, dataManager)

            def getExpectationAndSigma(self, numElements, inputData, *args):
                return (
                    np.zeros((2, 2)), np.ones((1, 2, 2)))

        dataManager = DataManager("TestDataManager")
        distribution = DistributionWithMeanAndVarianceTest(dataManager)

        samples = distribution.sampleFromDistribution(1, [])

    def test_sampleFromDistribution_given4DExpAndMultiSigma_expectValueError(
            self):
        class DistributionWithMeanAndVarianceTest(
                DistributionWithMeanAndVariance):

            def DistributionWithMeanAndVarianceTest(self, dataManager):
                DistributionWithMeanAndVariance.__init__(self, dataManager)

            def getExpectationAndSigma(self, numElements, inputData, *args):
                return (
                    np.ones((2, 5, 2, 2)), np.ones((1, 5, 2)))

        dataManager = DataManager("TestDataManager")
        distribution = DistributionWithMeanAndVarianceTest(dataManager)

        self.assertRaises(
            ValueError,
            distribution.sampleFromDistribution, 1, [])

    def test_sampleFromDistribution_givenExpAnd4DSigma_ValueError(
            self):
        class DistributionWithMeanAndVarianceTest(
                DistributionWithMeanAndVariance):

            def DistributionWithMeanAndVarianceTest(self, dataManager):
                DistributionWithMeanAndVariance.__init__(self, dataManager)

            def getExpectationAndSigma(self, numElements, inputData, *args):
                return (
                    np.zeros((1, 3, 3, 3)), np.zeros((1, 3, 3, 3)))

        dataManager = DataManager("TestDataManager")
        distribution = DistributionWithMeanAndVarianceTest(dataManager)

        self.assertRaises(
            ValueError,
            distribution.sampleFromDistribution,
            1,
            [])

    def test_getDataProbabilities_given3DExpAndDiagonalSigma_NoError(
            self):
        class DistributionWithMeanAndVarianceTest(
                DistributionWithMeanAndVariance):

            def DistributionWithMeanAndVarianceTest(self, dataManager):
                DistributionWithMeanAndVariance.__init__(self, dataManager)

            def getExpectationAndSigma(self, numElements, inputData, *args):
                return (np.zeros((2, 2, 1)), np.ones((2, 2, 1)))

        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 3)
        dataManager.addDataEntry("In", 3)
        distribution = DistributionWithMeanAndVarianceTest(dataManager)
        distribution.setOutputVariables(["Out"])
        distribution.setInputVariables(["In"])
        distribution.setDataProbabilityEntries()
        distribution.registerProbabilityNames("testLayer")

        qData = distribution.getDataProbabilities(None, np.zeros((2, 1, 3)))

    '''
    #TODO I was not sure if the branches in getDataProbabilities are doing the right thing
    # review them again and include if needed ^moritzs
    def test_getDataProbabilities_givenExpAndSingleVarianceMatrix_NoError(
            self):
        class DistributionWithMeanAndVarianceTest(
                DistributionWithMeanAndVariance):

            def DistributionWithMeanAndVarianceTest(self, dataManager):
                DistributionWithMeanAndVariance.__init__(self, dataManager)

            def getExpectationAndSigma(self, numElements, inputData, *args):
                # exp.shape=(1,1,3) simga.shape=(1,2,2)
                return (np.zeros((1, 1, 3)), np.expand_dims(
                    np.identity(2),
                    axis=0))

        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 3)
        dataManager.addDataEntry("In", 3)
        distribution = DistributionWithMeanAndVarianceTest(dataManager)
        distribution.setOutputVariables(["Out"])
        distribution.setInputVariables(["In"])
        distribution.setDataProbabilityEntries()
        distribution.registerProbabilityNames("testLayer")

        qData = distribution.getDataProbabilities(None, np.zeros((1, 1, 3)))

    def test_getDataProbabilities_given3DExpAndSingle3DSigmaMatrix_NoError(
            self):
        class DistributionWithMeanAndVarianceTest(
                DistributionWithMeanAndVariance):

            def DistributionWithMeanAndVarianceTest(self, dataManager):
                DistributionWithMeanAndVariance.__init__(self, dataManager)

            def getExpectationAndSigma(self, numElements, inputData, *args):
                return (np.zeros((1, 2, 2)), np.ones((3, 1, 2)))

        dataManager = DataManager("TestDataManager")
        dataManager.addDataEntry("Out", 3)
        dataManager.addDataEntry("In", 3)
        distribution = DistributionWithMeanAndVarianceTest(dataManager)
        distribution.setOutputVariables(["Out"])
        distribution.setInputVariables(["In"])
        distribution.setDataProbabilityEntries()
        distribution.registerProbabilityNames("testLayer")

        qData = distribution.getDataProbabilities(
            None,
            np.expand_dims(
                np.identity(2),
                axis=0))
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

if __name__ == '__main__':
    unittest.main()
