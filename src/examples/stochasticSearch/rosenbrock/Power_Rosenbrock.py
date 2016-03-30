import os
import sys
sys.path.insert(0, os.path.abspath("../../.."))

import numpy as np
from common.Settings import Settings
from distributions.gaussian.GaussianParameterPolicy import \
GaussianParameterPolicy
from environments.banditEnvironments.RosenbrockReward import RosenbrockReward
from environments.banditEnvironments.SinDistReward import SinDistReward
from experiments.Trial import Trial
from experiments.Trial import StoringType
from learner.episodicRL.EpisodicPower import EpisodicPower
from sampler.EpisodeSampler import EpisodeSampler


class PowerRosenbrock(Trial):

    def __init__(self, evalDir, trialIndex):
        super(PowerRosenbrock, self).__init__(evalDir, trialIndex)

    def configure(self):
        # set some basic parameters
        self.settings.setProperty("numParameters", 15)
        self.settings.setProperty("numContexts", 15)
        self.settings.setProperty("numSamplesEpisodes", 10)
        self.settings.setProperty("numIterations", 200)

        # create the sampler
        self.sampler = EpisodeSampler()
        self.dataManager = self.sampler.dataManager

        # add the reward function
        #self.returnSampler = RosenbrockReward(
        #    self.sampler,
        #    self.settings.getProperty('numContexts'),
        #    self.settings.getProperty('numParameters'))
        self.returnSampler = SinDistReward(self.sampler)

        # set the parameter policy
        self.parameterPolicy = GaussianParameterPolicy(self.dataManager)

        # create the policy learner
        self.policyLearner = EpisodicPower(self.dataManager, None)

        # set the parameter policy in the sampler
        self.sampler.setParameterPolicy(self.parameterPolicy)

        # set the return function in the sampler
        self.sampler.setReturnFunction(self.returnSampler)

        # mark the trail as ready for execution
        self.configured = True

    def run(self):
        if not self.configured:
            raise RuntimeError("The trial has to be configured first.")

        # create the data objects which store the data
        newData = self.dataManager.getDataObject(10)
        fullData = self.dataManager.getDataObject(0)

        # do all iterations
        for i in range(0, self.settings.getProperty('numIterations')):
            self.sampler.setSamplerIteration(i)

            # create new samples
            self.sampler.createSamples(newData)

            # keep old samples strategy comes here...
            fullData = newData
            #fullData.mergeData(newData);
            #deletionStrategy.deleteSamples(fullData)

            # data preprocessors come here
            # ...
            #importanceWeighting.preprocessData(data);

            # update the model in order to actually learn something
            self.policyLearner.updateModel(fullData)

            # store some basic values
            self.store('avgReturns', np.mean(newData.getDataEntry('returns')), StoringType.ACCUMULATE)
            '''
            % log the results...
            %self.store('entropy', policyLearner.entropyAfter, Experiments.StoringType.ACCUMULATE);
            self.store('divMean', policyLearner.divMean, Experiments.StoringType.ACCUMULATE);
            self.store('divCov', policyLearner.divCov, Experiments.StoringType.ACCUMULATE);
            %self.store('divKL', policyLearner.divKL, Experiments.StoringType.ACCUMULATE);
            '''

            # print some information about the current progress
            print(
                "Iteration: %d, Episodes: %d, AvgReturn: %f" %
                (i, i * self.settings.getProperty('numSamplesEpisodes'),
                 np.mean(newData.getDataEntry('returns'))))
