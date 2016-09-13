import math
import numpy as np
from pypost.envs.ContextualBlackBoxTask import ContextualBlackBoxTask

class SinDistReward(ContextualBlackBoxTask):
    def __init__(self, dataManager):
        ContextualBlackBoxTask.__init__(
            self, dataManager, 1, 1)

        #print(self.dimContext)
        self.dataManager.setRange('contexts',
                                  np.ones((self.dimContext)) * 0,
                                  np.ones((self.dimContext)) * (2*math.pi))
        self.dataManager.setRange('parameters',
                                  np.ones((self.dimParameters)) * -5, np.ones((self.dimParameters)) * 5)

    def sampleReturn(self, contexts, parameters):
        rewardTerm = -((parameters - np.sin(contexts))**2)
        contextFactor = (1 + np.cos(contexts) * 5)**2;
        reward = np.sum(rewardTerm*contextFactor, 1)
        return reward.reshape((reward.shape[0], 1))
