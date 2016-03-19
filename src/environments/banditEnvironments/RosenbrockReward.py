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
                                  -10 * np.ones(dimContext),
                                  +10 * np.ones(dimContext))

        self.dataManager.setRange('parameters',
                                  -5 * np.ones(dimParameters),
                                  +5 * np.ones(dimParameters));

        # self.linkProperty('rewardNoise');

    def sampleReturn(self, contexts, parameters):
        x = np.hstack((contexts, parameters))

        # rosenbrock = (1-x)^2 + 100*(y-x^2)^2
        reward = np.add(100 * np.sum((np.square(x[..., 1:-2]) -
                        np.square(x[..., 2:-1])), 2),
                        np.sum(np.square(x[..., 1:-2]-1), 2))

        # reward =sum(sample.^2,2);
        # reward = -1 * reward # / 10^5;

        return -reward
