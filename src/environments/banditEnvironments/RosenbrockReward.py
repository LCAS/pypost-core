import numpy as np
from environments.EpisodicContextualParameterLearningTask \
import EpisodicContextualParameterLearningTask


class RosenbrockReward(EpisodicContextualParameterLearningTask):
    def __init__(self, episodeSampler, dimContext, dimParameters):
        super().__init__(episodeSampler, dimContext, dimParameters)

        self.rewardCenter = 0
        self.rewardDistance = 0

        self.rewardNoise = 0
        self.rewardNoiseMult = 0

        self.dataManager.setRange('contexts',
                                  -100 * np.ones(dimContext),
                                  +100 * np.ones(dimContext))

        self.dataManager.setRange('parameters',
                                  -50 * np.ones(dimParameters),
                                  +50 * np.ones(dimParameters));

        # FIXME ASK how to initialize A
        self.A = np.ndarray((dimContext, dimContext))

        # self.linkProperty('rewardNoise');

    def sampleReturn(self, contexts, parameters):
        for i in range(0, parameters.shape[0]):
            vec = (contexts[i,:]).dot(self.A)
            print(contexts, self.A, vec, np.sin(vec), '\n\n', parameters)
            parameters[i,:] = parameters[i,:] +\
                              np.sin(vec)

        x = parameters;
        x = x.conj().T

        reward = 1e2*np.sum((x[0: -2, :]**2 - x[1: -1, :])**2, 1) + \
                 np.sum((x[1: -2, :]-1)**2, 1)

        reward = -1**(reward.conj().T)
