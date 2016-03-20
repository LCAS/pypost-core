import math
import numpy as np
from functions.FunctionLinearInFeatures import FunctionLinearInFeatures
from distributions.DistributionWithMeanAndVariance import \
DistributionWithMeanAndVariance
from parametricModels.ParametricModel import ParametricModel


class GaussianLinearInFeatures(FunctionLinearInFeatures,
    DistributionWithMeanAndVariance, ParametricModel):
    '''
    The  GaussianLinearInFeatures class models gaussian distributions where the
    mean can be a linear function of the feature vectors.

    This class models a linear Gaussian distribution in the form of
    \f$\mathcal{N}(\boldsymbol{y}| \boldsymbol{b} + \boldsymbol{W} \boldsymbol{\phi}(\boldsymbol{x}), \boldsymbol{\Sigma})\f$

    We omit the scaling scalar because we will work with normalized data.

    This class is a subclass of :class:`Distributions.DistributionWithMeanAndVariance`
    and defines the abstract :func:`getExpectationAndSigma` so this class acts
    like a Gaussian distribution in the functions :func:`sampleFromDistribution`
    and :func:`getDataProbabilities` of the superclass.

    Because of its numerical features this class will work via cholesky matrix
    internally, but is able to return characteristics like mean, expectation
    and the sigma matrix like expected.

    see Functions.Mapping for more information how to use outputVariable
    and inputVariables etc
    '''

    def __init__(self, dataManager, outputVariable, inputVariables,
                 functionName, featureGenerator=None, doInitWeights=None):
        '''
        Constructor

        :param dataManager: DataManager to operate on
        :param outputVariable: set of output Variables of the gaussian function
        :param inputVariables: set of input Variables of the gaussian function
        :param functionName: name of the gaussian function

        FIXME varargin
        :param varargin: optional featureGenerator, doInitWeights (see superclass Functions.FunctionLinearInFeatures)
        '''
        ParametricModel.__init__(self)
        FunctionLinearInFeatures.__init__(self, dataManager, outputVariable,
                                          inputVariables, functionName,
                                          featureGenerator, doInitWeights)
        DistributionWithMeanAndVariance.__init__(self, dataManager)

        self.saveCovariance = False
        self.initSigma = 0.1

        minRange = self.dataManager.getMinRange(self.outputVariable)
        maxRange = self.dataManager.getMaxRange(self.outputVariable)
        Range = np.subtract(maxRange, minRange)

        # Matrix in the Cholesky decomposition
        self.cholA = np.diag(Range * self.initSigma)

        # FIXME
        #self.indexForCov = []
        #index = 0
        #for i in range(0, self.dimOutput)
        #    self.indexForCov.append(index + (i:self.dimOutput))
        #    index = index + self.dimOutput

        #if (ischar(outputVariable))
        #    self.linkProperty('initSigma', ['initSigma',  #upper(self.outputVariable(1)), self.outputVariable(2:end)])
        #else
        #    self.linkProperty('initSigma')
        #end

        self.registerMappingInterfaceDistribution()
        self.registerMappingInterfaceFunction()
        self.registerGradientModelFunction()

    def getNumParameters(self):
        numParameters = LinearInFeatures.getNumParameters() +\
        self.numParameters + self.dimOutput * (self.dimOutput + 1) / 2


    def getSigma(self):
        # TODO: check this
        return self.cholA[1, ..., ...]

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
            self.cholA = chol(covMat)

    def setSigma(self, cholA):
        '''Set sigma

        :param cholA: The squareroot of the covariance in cholesky form
        '''
        if self.saveCovariance:
            self.cov = np.square(cholA)
        else:
            self.cholA = cholA

    def getSigma(self):
        if self.saveCovariance:
            return chol(self.covMat)
        else:
            return self.cholA

    def getJointGaussians(self, muInput, SigmaInput):
        muNew = np.hstack((muInput, self.bias + self.weights * muInput))

        tmp = self.weights.dot(SigmaInput).conj().T
        SigmaNew = np.vstack((np.hstack((SigmaInput, tmp)),
                              np.hstack(
                                tmp.conj().T,
                                self.getCovariance() + self.weights.dot(tmp))))

        return (nuNew, SigmaNew)

    def getGaussianFromJoint(self, muJoint, SigmaJoint):
        tmpN = self.dimInput
        muInput = muJoint[0:tmpN]
        SigmaInput = SigmaJoint[0:tmpN, 0:tmpN]

        SigmaInputOutput = SigmaJoint[0:tmpN, tmpN:-1] # TODO: check
        self.weights = np.linalg.lstsq(SigmaInput.T, SigmaInputOutput)
        self.bias = muJoint[tmpN:-1] - self.weights.dot(muInput)

        SigmaOutput = SigmaJoint[tmpN:-1, tmpN:-1] -\
                      self.weights.dot(SigmaInputOutput)
        self.setCovariance(SigmaOutput)

    def getLikelihoodGradient(self, inputMatrix, outputMatrix):
        expectation = self.getExpectation(inputMatrix.shape[0], inputMatrix)
        gradientFunction = self.getGradient(inputMatrix)

        n = outputMatrix.shape[0]
        d = outputMatrix.shape[1]
        zmx = outputMatrix - expectation
        C  = self.getCovariance()

        duplicate = inputMatrix.shape[1] + 1
        gradMeanFactor = np.linalg.lstsq(C.T, zmx.T)
        gradMeanFactor = np.tile(gradMeanFactor, (1, duplicate))
        gradMean = gradientFunction * gradMeanFactor

        gradCholA = np.zeros((n, d*(d+1)/2))

        for s in range(0, n):
            R = np.linalg.lstsq(
                    np.linalg.lstsq(
                        self.cholA.conj().T,
                        (zmx[s, :].conj().T).dot(zmx[s, :])).T,
                    C.T) - np.diag(np.diag(self.cholA)**-1)
            gradCholA[s,:] = R[self.indexForCov]

        return (gradMean, gradCholA)

    def getFisherInformationMatrix(self):
        noPars = self.numParameters
        d = self.dimOutput

        Fim = np.zeros((noPars, noPars))
        C = self.getCovariance()
        F0 = np.linalg.inv(C)
        Fim[0:d, 0:d] = F0

        ix_act = d+1
        ix_nxt = 2*d

        # TODO Check with Paper
        for k in range(0, d):
            f = np.zeros((d-k+1, d-k+1))
            f[0, 0] = math.pow(self.cholA[k, k], -2)
            D = F0[k:-1, k:-1]

            f = f + D

            Fim[ix_act:ix_nxt, ix_act:ix_nxt] = f

            dummy = ix_act
            ix_act = ix_nxt + 1
            ix_nxt = ix_nxt + (ix_nxt - dummy)

        return Fim

    def setParameterVector(self, theta):
        self.setParameterVector(theta)
        theta = theta[self.dimOutput.dot(1 + self.dimInput):-1]
        self.cholA[self.indexForCov] = theta


    def getParameterVector(self):
        # Replaced the following line, not sure if legal syntax?
        #theta = self.getParameterVector@Functions.FunctionLinearInFeatures()
        theta = super(GaussianLinearInFeatures, self).getParameterVector()
        return np.hstack((theta, self.cholA[self.indexForCov]))

    def getExpectationAndSigma(self, numElements, *args):
        print('*args: ', args)
        mean = FunctionLinearInFeatures.getExpectation(self, numElements, *args)

        sigma[1,:, :] = self.cholA

        return (mean, sigma)
