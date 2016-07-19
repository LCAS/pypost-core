import os
import sys
from pypost.common import SettingsManager

import numpy as np
from pypost.common.Settings import Settings
from pypost.distributions.gaussian.GaussianParameterPolicy import \
GaussianParameterPolicy
from pypost.environments.banditEnvironments.RosenbrockReward import RosenbrockReward
from pypost.environments.banditEnvironments.SinDistReward import SinDistReward
from pypost.experiments.Trial import Trial
from pypost.experiments.Trial import StoringType
from pypost.learner.episodicRL.EpisodicPower import EpisodicPower
from pypost.learner.episodicRL.NESLearner2 import NESLearner2
from pypost.sampler.EpisodeSampler import EpisodeSampler


class NESRosenbrock(Trial):

    def __init__(self, evalDir, trialIndex):
        super(NESRosenbrock, self).__init__(evalDir, trialIndex)

    def configure(self):
        # set some basic parameters
        self.dsettings = SettingsManager.getDefaultSettings()
        self.dsettings.setProperty("numParameters", 15)
        self.dsettings.setProperty("numContexts", 0)
        self.dsettings.setProperty("numSamplesEpisodes", 15)
        self.dsettings.setProperty("numIterations", 200)
        self.dsettings.setProperty("L", 15)

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

        self.policyLearner = NESLearner2(
            self.dataManager, self.parameterPolicy)
        # create the policy learner
        #self.policyLearner = EpisodicPower(self.dataManager, None)

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
        newData = self.dataManager.getDataObject(0)

        # do all iterations
        for i in range(0, self.dsettings.getProperty('numIterations')):
            # create new samples
            self.sampler.createSamples(newData)

            # keep old samples strategy comes here...
            #data = newData
            #fullData.mergeData(newData);
            #deletionStrategy.deleteSamples(fullData)

            # data preprocessors come here
            # ...
            #importanceWeighting.preprocessData(data);

            # update the model in order to actually learn something
            self.policyLearner.updateModel(newData)

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
                (i, i * self.dsettings.getProperty('numSamplesEpisodes'),
                 np.mean(newData.getDataEntry('returns'))))