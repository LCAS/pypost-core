import math
import numpy as np
from functions.FunctionLinearInFeatures import FunctionLinearInFeatures
from distributions.DistributionWithMeanAndVariance import \
    DistributionWithMeanAndVariance
from parametricModels.ParametricModel import ParametricModel
from common.SettingsClient import SettingsClient


class GaussianLinearInFeatures(FunctionLinearInFeatures,
                               DistributionWithMeanAndVariance, ParametricModel,
                               SettingsClient):
    '''
    The  GaussianLinearInFeatures class models gaussian distributions where the
    mean can be a linear function of the feature vectors.

    We omit the scaling scalar because we will work with normalized data.

    This class is a subclass of :class:`distributions.DistributionWithMeanAndVariance`
    and defines the abstract :func:`getExpectationAndSigma` so this class acts
    like a Gaussian distribution in the functions :func:`sampleFromDistribution`
    and :func:`getDataProbabilities` of the superclass.

    Because of its numerical features this class will work via cholesky matrix
    internally, but is able to return characteristics like mean, expectation
    and the sigma matrix like expected.

    see functions.Mapping for more information how to use outputVariables
    and inputVariables etc
    '''

    def __init__(self, dataManager, outputVariables, inputVariables,
                 functionName, featureGenerator=None, doInitWeights=True):
        '''
        Constructor

        :param dataManager: DataManager to operate on
        :param outputVariables: set of output Variables of the gaussian function
        :param inputVariables: set of input Variables of the gaussian function
        :param functionName: name of the gaussian function
        '''
        ParametricModel.__init__(self)
        DistributionWithMeanAndVariance.__init__(self, dataManager)
        FunctionLinearInFeatures.__init__(self, dataManager, outputVariables,
                                          inputVariables, functionName,
                                          featureGenerator, doInitWeights)
        SettingsClient.__init__(self)

        self.saveCovariance = False
        self.initSigma = 0.1

        minRange = self.dataManager.getMinRange(self.outputVariables[0])
        maxRange = self.dataManager.getMaxRange(self.outputVariables[0])
        Range = np.subtract(maxRange, minRange)

        # Matrix in the Cholesky decomposition
        self.cholA = np.diag(Range * self.initSigma)

        self.numParameters = 0

        # NOTE: indexForCov is not needed and therefore not calculated
        #self.indexForCov = []
        #index = 0
        # for i in range(0, self.dimOutput)
        #    self.indexForCov.append(index + (i:self.dimOutput))
        #    index = index + self.dimOutput

        if isinstance(outputVariables[0], str):
            self.linkProperty('initSigma', 'initSigma' +
                              self.outputVariables[0].capitalize())
        else:
            self.linkProperty('initSigma')

        self._registerMappingInterfaceDistribution()
        self.registerMappingInterfaceFunction()
        self.registerGradientModelFunction()

    def getNumParameters(self):
        numParameters = FunctionLinearInFeatures.getNumParameters(
            self) + self.numParameters + self.dimOutput * (self.dimOutput + 1) / 2
        return numParameters

    def getCovariance(self):
        '''
        Return the covariance matrix
        '''
        if self.saveCovariance:
            return self.covMat
        else:
            return self.cholA * self.cholA

    def getMean(self):
        '''
        Return the bias vector
        '''
        return self.bias

    def setCovariance(self, covMat):
        if (self.saveCovariance):
            self.covMat = covMat
        else:
            # np returns L but Matlab is returning R -> transpose
            self.cholA = np.transpose(np.linalg.cholesky(covMat))

    def setSigma(self, cholA):
        '''Set sigma

        :param cholA: The squareroot of the covariance in cholesky form
        '''
        if self.saveCovariance:
            self.covMat = np.square(cholA)
        else:
            self.cholA = cholA

    def getSigma(self):
        if self.saveCovariance:
            return np.transpose(np.linalg.cholesky(self.covMat))
        else:
            # np returns L but Matlab is returning R -> transpose
            return self.cholA

    def getExpectationAndSigma(self, numElements, *args):
        mean = FunctionLinearInFeatures.getExpectation(
            self,
            numElements,
            *args)

        sigma = np.ndarray((1,) + self.cholA.shape)
        sigma[0, :, :] = self.cholA

        return (mean, sigma)
