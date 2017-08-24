import numpy as np
from pypost.common.SettingsClient import SettingsClient
from pypost.envs.ContextualBlackBoxTask import ContextualBlackBoxTask


class RosenbrockReward(ContextualBlackBoxTask): #pragma nocover
    def __init__(self, dataManager, numContexts, numParameters):
        ContextualBlackBoxTask.__init__(
            self, dataManager, numContexts, numParameters)
        SettingsClient.__init__(self)

        self.rewardCenter = 0
        self.rewardDistance = 0

        self.rewardNoise = 0
        self.rewardNoiseMult = 0

        self.dataManager.setRange('contexts',
                                  -100 * np.ones(numContexts),
                                  +100 * np.ones(numContexts))

        self.dataManager.setRange('parameters',
                                  -50 * np.ones(numParameters),
                                  +50 * np.ones(numParameters));

        self.A = np.random.randn(numContexts, numParameters) +\
                 3 * np.ones((numContexts, numParameters))

        self.linkPropertyToSettings('rewardNoise')

    def sampleReturn(self, contexts, parameters):
        for i in range(0, parameters.shape[0]):
            vec = (contexts[i,:]).dot(self.A)
            parameters[i,:] = parameters[i,:] +\
                              np.sin(vec)

        reward = 1e2*np.sum((parameters[:, 0: -1]**2 - parameters[:, 1:])**2, 1) + \
                 np.sum((parameters[:, 0: -1]-1)**2, 1)

        if len(reward.shape) >= 2:
            reward = -1*(reward.conj().T)
        else:
            reward = -1*(reward[np.newaxis, :].T)

        if reward.shape[0] == 1:
            reward = reward[0]


        return reward

if __name__ == "__main__":
    rosenBrock = RosenbrockReward(0,1)
    lala = rosenBrock