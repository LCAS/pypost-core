import numpy as np

from pypost.learner.LinearFeatureFunctionMLLearner import LinearFeatureFunctionMLLearner
from pypost.learner.utils import boundCovariance, regularizeCovariance
from pypost.mappings import FullGaussian_Base
from pypost.mappings import DiagonalGaussian_Base

class LinearGaussianMLLearner(LinearFeatureFunctionMLLearner):
    '''
    The < tt > LinearGaussianMLLearner < / tt > fits a linear model and a full covariance matrix given regression data.
    The class has the following properties that can be changed over the Settings interface:
        - < tt > maxCorr < / tt > (default 1): maximum correlation coefficient in the covariance matrix.
        - < tt > minCov < / tt > (default 10 ^ -12): minimal covariance of the diagonal elements in the sigma matrix
        - < tt > priorCov < / tt > (default 1): prior used for the fit. Can be seen as shrinkage matrix.
        - < tt > priorCovWeight < / tt > (default 10 ^ -16): factor of the prior (in terms of number of samples)
    '''
    def __init__(self, dataManager, gaussian,  weightName = None, inputVariables = None, outputVariable = None):
        '''
        :param dataManager:
        :param functionApproximator:
        :param weightName:
        :param inputVariables:
        :param outputVariable:
        '''


        LinearFeatureFunctionMLLearner.__init__(self, dataManager, gaussian.meanFunction,  weightName, inputVariables, outputVariable)

        self.minCov = 10 ** -12
        self.priorCov = 1.0
        self.priorCovWeight = 10 ** -16
        self.KL = 0
        self.gaussian = gaussian

        mapName = gaussian.outputVariables[0]
        mapName = mapName[0].upper() + mapName[1:]

        #self.linkProperty('maxCorr', 'maxCorr' + mapName)
        self.linkPropertyToSettings('minCov', globalName = 'minCov' + mapName)
        self.linkPropertyToSettings('priorCov', globalName = 'priorCov' + mapName)
        self.linkPropertyToSettings('priorCovWeight', globalName = 'priorCovWeight' + mapName)


    def updateModel(self, inputData, outputData, weighting = None):

        if inputData.shape[0] == 0:
            inputData = np.zeros((outputData.shape[0], 0))

        if weighting is None:
            weighting = np.ones((inputData.shape[0], 1))

        super(LinearGaussianMLLearner, self).updateModel(inputData, outputData, weighting)

        sumW = weighting.sum()
        weighting = weighting / sumW

        Z = 1 - np.dot(weighting.transpose(), weighting)

        priorCov = self.priorCov
        priorCovWeight = self.priorCovWeight
        rangeOutput = self.dataManager.getMaxRange(self.functionApproximator.outputVariables[0]) - self.dataManager.getMinRange(self.functionApproximator.outputVariables[0])


        if Z > 0:
            expectedOutput = self.functionApproximator(inputData)

            difference = expectedOutput - outputData
            differenceW = difference * weighting

            if isinstance(self.gaussian, FullGaussian_Base):

                SigmaA = np.dot(difference.transpose(), differenceW)

                SigmaA = 1 / Z * SigmaA

                minCov = self.minCov * rangeOutput

                numEffectiveSamples = 1.0 / weighting.max()

                SigmaA = boundCovariance(SigmaA, minCov)
                SigmaA, cholA = regularizeCovariance(SigmaA, np.diag(rangeOutput) * priorCov, numEffectiveSamples, priorCovWeight)

                self.gaussian.param_stdmat = cholA.transpose()
            elif  isinstance(self.gaussian, DiagonalGaussian_Base):

                varA = np.sum(difference * differenceW, axis=0) / Z

                self.gaussian.param_logstd = 0.5 * np.log(varA.reshape(self.gaussian.param_logstd))
