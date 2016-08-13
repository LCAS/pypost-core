import unittest

import numpy as np
from numpy.random import normal
from numpy.random import uniform

from pypost.data.DataManager import DataManager
from pypost.distributions.GaussianLinearInFeatures import GaussianLinearInFeatures
from pypost.learner.supervisedLearner.LinearGaussianMLLearner import LinearGaussianMLLearner


class testLinearGaussianMLLearner(unittest.TestCase):

    def testLinearGaussianMLLearner(self):

        dimInput = 3
        dimOutput = 2
        dataManager = DataManager('data')
        dataManager.addDataEntry('inputs', dimInput)
        dataManager.addDataEntry('outputs', dimOutput)
        dataManager.addDataEntry('weights', 1)

        numSamples = 1000000
        data = dataManager.getDataObject([numSamples])

        gaussianDist = GaussianLinearInFeatures(dataManager, ['inputs'], 'outputs', 'testFunction')
        gaussianDistLearner = LinearGaussianMLLearner(dataManager, gaussianDist)

        meanVec = normal(0, 1,(dimOutput,1))
        betaVec = normal(0, 1, (dimOutput, dimInput))

        covMat = normal(0, 1, (dimOutput, dimOutput))
        covMat = np.dot(covMat.transpose(), covMat)

        gaussianDist.setCovariance(covMat)
        gaussianDist.setWeightsAndBias(betaVec, meanVec)


        inputVectors = normal(0, 1, (numSamples, dimInput))

        outputVectors = gaussianDist.sampleFromDistribution(inputVectors)
        weights = uniform(0,1, (numSamples,1))

        data.setDataEntry('inputs', [], inputVectors)
        data.setDataEntry('outputs', [], outputVectors)
        data.setDataEntry('weights', [], weights)

        gaussianDistLearner.setWeightName('weights')
        gaussianDistLearner.updateModel_fromData(data)

        meanVecLearned = gaussianDist.getMean()
        betaVecLearned = gaussianDist.getBeta()

        covMatLearned = gaussianDist.getCovariance()

        self.assertTrue(np.sum(np.square(meanVec - meanVecLearned)) < 0.01)
        self.assertTrue(np.sum(np.square(betaVec - betaVecLearned)) < 0.01)

        self.assertTrue(np.sum(np.square(covMat - covMatLearned)) < 0.05)


if __name__ == '__main__':
    unittest.main()
