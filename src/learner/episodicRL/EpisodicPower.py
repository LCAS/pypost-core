import numpy as np

from learner.weightedML.RLByWeightedML import RLByWeightedML


class EpisodicPower(RLByWeightedML):
    '''
    Implementation of an episodic PoWER algorithm
    '''

    def __init__(self, dataManager, policyLearner):
        '''
        Constructor
        '''

        RLByWeightedML.__init__(self, dataManager, policyLearner)

        # TODO find default value
        self.divKL = None

        self.temperatureScalingPower = 10.0

        # FIXME linkProperty
        #self.linkProperty('temperatureScalingPower')

    def computeWeighting(self, rewards):
        maxQ = np.max(rewards)
        minQ = np.min(rewards)

        weighting = np.exp(
            self.temperatureScalingPower * (rewards - maxQ) / ((maxQ - minQ) + 10e-6))
        weighting = weighting / np.sum(weighting)

        self.divKL = self.getKLDivergence(
            np.ones(
                np.size(weighting)),
            weighting)

        return weighting

    def printMessage(self, data):
        # FIXME completely overwrites RLLearner printMessage include this also?
        print("divKL: %f", self.divKL)
