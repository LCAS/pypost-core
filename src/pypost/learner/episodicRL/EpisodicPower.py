import numpy as np

from pypost.common.SettingsClient import SettingsClient
from pypost.data import *
from pypost.learner.episodicRL.RLByWeightedML import RLByWeightedML


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

        self.divKL = 0
        self.temperatureScalingPower = 10.0

        self.linkProperty('temperatureScalingPower')

    def computeWeighting(self, rewards):
        maxQ = np.max(rewards)
        minQ = np.min(rewards)

        weighting = np.exp(self.temperatureScalingPower * (rewards - maxQ) / ((maxQ - minQ) + 10e-6))
        weighting = weighting / np.sum(weighting)

        self.divKL = self.getKLDivergence(np.ones(np.size(weighting)), weighting)

        return weighting

    def printMessage(self, data):
        print("divKL: %f", self.divKL)
