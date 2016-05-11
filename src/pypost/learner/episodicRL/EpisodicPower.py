import numpy as np

from pypost.learner.weightedML.RLByWeightedML import RLByWeightedML
from pypost.common.SettingsClient import SettingsClient


class EpisodicPower(RLByWeightedML, SettingsClient):
    '''
    Implementation of an episodic PoWER algorithm
    '''

    def __init__(self, dataManager, policyLearner):
        '''
        Constructor
        '''
        RLByWeightedML.__init__(self, dataManager, policyLearner)
        SettingsClient.__init__(self)

        # TODO find default value
        self.divKL = None

        self.temperatureScalingPower = 10.0

        self.linkProperty('temperatureScalingPower')

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
