import os
import sys
sys.path.insert(0, os.path.abspath("../../.."))

import numpy as np
from common.Settings import Settings
from distributions.gaussian.GaussianParameterPolicy import \
GaussianParameterPolicy
from environments.banditEnvironments.RosenbrockReward import RosenbrockReward
from experiments.Trial import Trial
from experiments.Trial import StoringType
from learner.episodicRL.EpisodicPower import EpisodicPower
from sampler.EpisodeSampler import EpisodeSampler


class PowerRosenbrock(Trial):

    def __init__(self, evalDir, trialIndex):
        super(PowerRosenbrock, self).__init__(evalDir, trialIndex)

    def configure(self):
        self.settings.setProperty("numParameters", 15)
        self.settings.setProperty("numContexts", 15)
        self.settings.setProperty("numSamplesEpisodes", 10)
        self.settings.setProperty("numIterations", 2000)

        self.sampler = EpisodeSampler()
        self.dataManager = self.sampler.dataManager # TODO is this OK?

        self.returnSampler = RosenbrockReward(
            self.sampler,
            self.settings.getProperty('numContexts'),
            self.settings.getProperty('numParameters'))

        self.parameterPolicy = GaussianParameterPolicy(self.dataManager)
        self.policyLearner = EpisodicPower(self.dataManager, None)

        # FIXME None should be a policyLearner instance ... is this parameter even used?
        # from the outcommented CreateFromTrial function in EpisodicPower we
        # would set trial.parameterPolicyLearner and trial.dataManager

        self.sampler.setParameterPolicy(self.parameterPolicy)
        self.sampler.setReturnFunction(self.returnSampler)

        self.configured = True

    def run(self):
        if not self.configured:
            raise RuntimeError("The trial has to be configured first.")

        newData = self.dataManager.getDataObject(10)
        fullData = self.dataManager.getDataObject(0)

        for i in range(0, self.settings.getProperty('numIterations')):
            self.sampler.setSamplerIteration(i)
            self.sampler.createSamples(newData)

            # keep old samples strategy comes here...
            fullData = newData
            #fullData.mergeData(newData);
            #deletionStrategy.deleteSamples(fullData)

            # data preprocessors come here
            # ...
            #importanceWeighting.preprocessData(data);

            # learning comes here...
            self.policyLearner.updateModel(fullData)

            #print(newData.getDataEntry('returns'), np.mean(newData.getDataEntry('returns')))
            self.store('avgReturns', np.mean(newData.getDataEntry('returns')), StoringType.ACCUMULATE)
            '''
            % log the results...
            %self.store('entropy', policyLearner.entropyAfter, Experiments.StoringType.ACCUMULATE);
            self.store('divMean', policyLearner.divMean, Experiments.StoringType.ACCUMULATE);
            self.store('divCov', policyLearner.divCov, Experiments.StoringType.ACCUMULATE);
            %self.store('divKL', policyLearner.divKL, Experiments.StoringType.ACCUMULATE);
            '''

            # FIXME Test if this works
            #trial.store("avgReturns",np.mean(newData.getDataEntry("returns")), Experiments.StoringType.ACCUMULATE)

            print(
                "Iteration: %d, Episodes: %d, AvgReturn: %f" %
                (i, i * self.settings.getProperty('numSamplesEpisodes'),
                 np.mean(newData.getDataEntry('returns'))))


# For testing purposes. Maybe implement a better way to start trials directly?
#power_rosenbrock = PowerRosenbrock("/tmp/trial/", 0)
#power_rosenbrock.start()
