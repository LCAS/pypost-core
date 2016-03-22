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
            #print(contexts, self.A, vec, np.sin(vec), '\n\n', parameters)
            parameters[i,:] = parameters[i,:] +\
                              np.sin(vec)

        x = parameters
        x = x[np.newaxis, :].T

        # FIXME: reward doesn't make any sense.
        #print('x', x)
        #print('a', 1e2*np.sum((x[0: -2, :]**2 - x[1: -1, :])**2, 1))
        #print('b', np.sum((x[0: -2, :]-1)**2, 1))

        reward = 1e2*np.sum((x[0: -2, :]**2 - x[1: -1, :])**2, 1) + \
                 np.sum((x[0: -2, :]-1)**2, 1)

        # FIXME: this is a fake reward that matches the expected shape:
        reward = 1e2*np.sum((x[3: -2, :]**2 - x[4: -1, :])**2, 1) + \
                 np.sum((x[3: -2, :]-1)**2, 1)

        reward = -1**(reward[np.newaxis, :].T)

        return reward
