import math
import numpy as np
from environments.EpisodicContextualParameterLearningTask \
import EpisodicContextualParameterLearningTask

class SinDistReward(EpisodicContextualParameterLearningTask):
    def __init__(self, episodeSampler):
        EpisodicContextualParameterLearningTask.__init__(
            self, episodeSampler, 1, 1)

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
