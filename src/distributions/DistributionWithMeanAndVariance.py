import math
import numpy as np
from distributions.Distribution import Distribution
from data.DataManipulatorInterface import CallType


class DistributionWithMeanAndVariance(Distribution):
    '''
    The DistributionWithMeanAndVariance is a subclass of Distribution and
    augments the superclass with Mean and Variance.

    This class defines `sampleFromDistribution()` and `getDataProbabilities()`,
    since this is a subclass of Distribution. The output of these functions
    depends on the abstract function `getExpectationAndSigma()`,
    which will determine the type of distribution in further subclasses.

    The abstract function `getExpectationAndSigma(self, numElements, *args)`
    is expected to return the following types of data:

    - mean: Should be a matrix of size equal to numElements x dimension
    denoting the expectation of the distribution given the inputData.
    - sigma: should be a 3 dimensional array, where the first dimension
    indicates the numElements and the last 2 dimensions contain
    the sigma matrices for the corresponding samples. There are 3 different types of
    sigma this class can handle:
     + 1. Case: If the third dimension of the sigma matrix is 1, the
    class expects those values to be the diagonal variance.
     + 2. Case: If the first dimension of sigma is 1, there is only one
    sigma matrix for all elements. Then the class uses this sigma matrix
    for every sample.
     + 3. Case (default): Every Element has its own sigma matrix and will
    be handled as such.
    '''

    def __init__(self, dataManager):
        Distribution.__init__(self, dataManager)

    def sampleFromDistribution(self, numElements, *args):
        '''
        FIXME: varargin
        :param varargin: parameter for the abstract `getExpectationAndSigma()`
                         function. The first parameter is always `numElements`,
                         the rest is dependent on the subclass you are using
                         returns a number of random samples of the distribution
                         determined by the first parameter
        '''
        samples = None

        (expectation, sigma) = self.getExpectationAndSigma(numElements,
                                                           *args)

        if sigma.shape[2] == 1:
            # If the second dimension of the sigma matrix is 1, the
            # function expects those values to be the diagonal variance.
            # TODO: np.random.randn is not deterministic, MatLab's randn is
            samples = expectation + np.random.randn(
                expectation.shape[0], expectation.shape[1]) * sigma
        else:
            if sigma.shape[0] == 1:
                # If the first dimension of sigma is 1, there is only
                # one sigma matrix for all elements. Then we will
                # use this sigma matrix for every sample.
                sigma = np.transpose(sigma, (1, 2, 0))

                if len(expectation.shape) == 2:
                    expectRand = np.random.randn(
                        expectation.shape[0], expectation.shape[1])
                elif len(expectation.shape) == 3:
                    expectRand = np.random.randn(
                        expectation.shape[0], expectation.shape[1],
                        expectation.shape[2])
                else:
                    raise ValueError(
                        'expectation has an unsupported shape length')

                if sigma.shape[2] == 1:
                    sigma = sigma[0]

                samples = expectation + expectRand.dot(sigma)
            else:
                # Every Element has its own sigma matrix
                samples = expectation
                for i in range(0, samples.shape[0]):
                    samples[i, :] = samples[i, :] + np.random.randn(
                        1, expectation.shape[1]).dot(
                            np.transpose(sigma[i, :, :], (1, 2, 0)))

        return samples

    def getDataProbabilities(self, inputData, outputData, *args):
        '''
        :param inputData: vector of input data
        :param outputData: vector of output data
        :param varargin: used in `getExpectationAndSigma()`. Returns a vector
                         of the probability of inputData resulting in
                         outputData.
        '''
        (expectation, sigma) = self.getExpectationAndSigma(outputData.shape[0],
                                                           inputData,
                                                           *args)

        samples = None
        qData = None

        minRange = self.getDataManager().getMinRange(self.outputVariable)
        maxRange = self.getDataManager().getMaxRange(self.outputVariable)
        # TODO: check this:
        expectation = lambda: max(min(expectation, maxRange), minRange)

        if sigma.shape[2] == 1:
            # If the second dimension of the sigma matrix is 1, the
            # function expects those values to be the diagonal variance.

            samples = outputData - expectation
            samples = samples / sigma

            qData = -sum(math.log(sigma), 2)
        else:
            # If the first dimension of sigma is 1, there is only
            # one sigma matrix for all elements. Then we will
            # use this sigma matrix for every sample.
            if sigma.shape[0] == 1:
                samples = outputData - expectation
                sigma = np.transpose(sigma, (2, 3, 1))
                samples = np.linalg.lstsq(sigma.T, samples.T)

                # Here we do not need the 0.5 as it is the standard deviation
                qData = -sum(math.log(np.linalg.eig(sigma)[0]))
            else:
                # Every Element has its own sigma matrix
                samples = outputData - expectation
                qData = np.zeros(samples.shape[0])
                for i in range(0, samples.shape[0]):
                    sigma_tmp = np.transpose(sigma[i, :, :], (2, 3, 1))
                    samples[i, :] = samples[i, :] / sigma_tmp
                    qData[i] = -sum(math.log(np.linalg.eig(sigma_tmp)[0]))

        samplesDist = sum(samples**2, 2)
        # samplesDist = samplesDist - min(samplesDist)
        qData = -0.5 * samplesDist + qData - expectation.shape[1]/2 *\
                math.log(2*math.pi) # Misssing 2 pi?

        return qData

    def registerMappingInterfaceDistribution(self):
        Distribution.registerMappingInterfaceDistribution(self)

        if self.registerDataFunctions:
            self.addDataManipulationFunction(
                self.getExpectationAndSigma,
                [self.inputVariables, self.additionalInputVariables],
                [self.outputVariable[0]+'Mean', self.outputVariable[0]+'Std'],
                CallType.ALL_AT_ONCE, True)


    def getExpectationAndSigma(self, numElements, inputData, *args):
        # return mean, sigma
        # Check how this function is expected to behave in the documentation of this class
        raise NotImplementedError()
