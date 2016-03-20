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

        # self.linkProperty('rewardNoise');

    def sampleReturn(self, contexts, parameters):
        x = np.hstack((contexts, parameters))
        
        # FIXME(Sebastian): Pretty sure this computation is wrong here...
        #                   I think the output value should be a single value, not 8.

        # rosenbrock = (1-x)^2 + 100*(y-x^2)^2
        reward = np.sum(100 * np.sum((np.square(x[0:-2, :]) -
                        np.square(x[1:-1, :])), 1) + 
                        np.sum(np.square(x[0:-2, :]-1), 1))
        
        print("Reward: ", reward)

        # reward =sum(sample.^2,2);
        # reward = -1 * reward # / 10^5;

        return -reward
