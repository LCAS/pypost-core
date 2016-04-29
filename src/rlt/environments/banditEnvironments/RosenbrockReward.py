import numpy as np
from rlt.common.SettingsClient import SettingsClient
from rlt.environments.EpisodicContextualParameterLearningTask \
import EpisodicContextualParameterLearningTask


class RosenbrockReward(EpisodicContextualParameterLearningTask, SettingsClient): #pragma nocover
    def __init__(self, episodeSampler, dimContext, dimParameters):
        EpisodicContextualParameterLearningTask.__init__(
            self, episodeSampler, dimContext, dimParameters)
        SettingsClient.__init__(self)

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

        self.A = np.random.randn((dimContext, dimParameters)) +\
                 3 * np.ones((dimContext, dimParameters))

        self.linkProperty('rewardNoise')

    def sampleReturn(self, contexts, parameters):
        for i in range(0, parameters.shape[0]):
            vec = (contexts[i,:]).dot(self.A)
            parameters[i,:] = parameters[i,:] +\
                              np.sin(vec)

        x = contexts
        if len(contexts.shape) >= 2:
            x = x.conj().T
        else:
            x = x[np.newaxis, :].T

        #print(parameters, x)

        # FIXME: reward doesn't make any sense.
        reward = 1e2*np.sum((x[0: -2, :]**2 - x[1: -1, :])**2, 1) + \
                 np.sum((x[0: -2, :]-1)**2, 1)

        # FIXME: this is a fake reward that matches the expected shape:
        reward = 1e2*np.sum((x[3: -2, :]**2 - x[4: -1, :])**2, 1) + \
                 np.sum((x[3: -2, :]-1)**2, 1)

        if len(reward.shape) >= 2:
            reward = -1*(reward.conj().T)
        else:
            reward = -1*(reward[np.newaxis, :].T)

        if reward.shape[0] == 1:
            reward = reward[0]

        #print(reward)

        return reward
