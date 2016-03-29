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
        :param *args: parameter for the abstract `getExpectationAndSigma()`
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
            samples = expectation + np.random.randn(
                expectation.shape[0], expectation.shape[1]) * sigma[0, 0, 0]
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

                sigma = sigma[0]

                samples = expectation + expectRand.dot(sigma)
            else:
                raise NotImplementedError("Not implemented. See code")
                #
                # Every Element has its own sigma matrix
                #samples = expectation
                # for i in range(0, samples.shape[0]):
                #    samples[i, :] = samples[i, :] + np.random.randn(
                #        1, expectation.shape[1]).dot(
                #            np.transpose(sigma[i, :, :], (1, 2, 0)))

        return samples

    def getDataProbabilities(self, inputData, outputData, *args):
        '''
        :param inputData: vector of input data
        :param outputData: vector of output data
        :param *args: used in `getExpectationAndSigma()`. Returns a vector
                         of the probability of inputData resulting in
                         outputData.
        '''
        (expectation, sigma) = self.getExpectationAndSigma(outputData.shape[0],
                                                           inputData,
                                                           *args)

        samples = None
        qData = None

        # TODO this is failing for some of the branches below.
        # make sure to invoke this, only for cases were it works
        #minRange = self.dataManager.getMinRange(self.outputVariables[0])
        #maxRange = self.dataManager.getMaxRange(self.outputVariables[0])
        #expectation = np.maximum(np.minimum(expectation, maxRange), minRange)

        samples = outputData - expectation

        if sigma.shape[2] == 1:
            # If the second dimension of the sigma matrix is 1, the
            # function expects those values to be the diagonal variance.
            samples = samples / sigma

            qData = -sum(np.log(sigma), 2)
        else:  # pragma: no cover
            # If the first dimension of sigma is 1, there is only
            # one sigma matrix for all elements. Then we will
            # use this sigma matrix for every sample.

            # FIXME not quite sure if this does the right thing, review again,
            # before including this code - (also remove no cover pragma after doing
            # this) ^moritz
            raise NotImplementedError()

        samplesDist = sum(samples**2, 2)
        # samplesDist = samplesDist - min(samplesDist)
        qData = -0.5 * samplesDist + qData - expectation.shape[1] / 2 *\
            math.log(2 * math.pi)  # Misssing 2 pi?

        return qData

    def _registerMappingInterfaceDistribution(self):
        Distribution._registerMappingInterfaceDistribution(self)

        if self.registerDataFunctions:
            self.addDataManipulationFunction(
                self.getExpectationAndSigma,
                self.inputVariables,
                # + self.additionalInputVariables, #TODO check if these are used anywhere
                [self.outputVariables[0][0] +
                 'Mean', self.outputVariables[0][0] +
                 'Std'],
                CallType.ALL_AT_ONCE, True)

    def getExpectationAndSigma(self, numElements, inputData, *args):
        raise NotImplementedError()
