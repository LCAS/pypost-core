import numpy as np

import pypost.envs.banditEnvironments

from pypost.experiments.Trial import TrialStoringType
from pypost.experiments.Trial import Trial
from pypost.learner.episodicRL.NES import NaturalEvolutionStrategy
from pypost.sampler.EpisodeSampler import EpisodeSampler
from pypost.mappings.GaussianLinearInFeatures import GaussianLinearInFeatures
from pypost.envs.banditEnvironments.RosenbrockReward import RosenbrockReward



class PowerRosenbrock(Trial):

    def __init__(self, evalDir, trialIndex, trialSettings = None):
        super(PowerRosenbrock, self).__init__(evalDir, trialIndex, trialSettings)

    def _configure(self):
        # set some basic parameters

        self.settings.setProperty("numParameters", 2)
        self.settings.setProperty("numContexts", 0)
        self.settings.setProperty("numSamplesEpisodes", 10)
        self.settings.setProperty("numIterations", 200)

        # Apply external settings

        self.applyTrialSettings()

        # create the sampler
        self.sampler = EpisodeSampler()
        self.dataManager = self.sampler.dataManager

        # add the reward function
        self.returnSampler = RosenbrockReward(
            self.dataManager,
            self.settings.getProperty('numContexts'),
            self.settings.getProperty('numParameters'))
        #self.returnSampler = SinDistReward(self.sampler)

        # set the parameter policy
        self.parameterPolicy = GaussianLinearInFeatures(self.dataManager, inputVariables=['contexts'], outputVariables=['parameters'], name = 'parameterPolicy')

        # create the policy learner
        self.policyLearner = NaturalEvolutionStrategy(self.dataManager, self.parameterPolicy)

        # set the parameter policy in the sampler
        self.sampler.setParameterPolicy(self.parameterPolicy)

        # set the return function in the sampler
        self.sampler.setReturnFunction(self.returnSampler)

        # mark the trail as ready for execution
        self.configured = True

    def _run(self):
        if not self.configured:
            raise RuntimeError("The trial has to be configured first.")

        # create the data objects which store the data
        newData = self.dataManager.getDataObject(10)
        fullData = self.dataManager.getDataObject(0)

        # do all iterations
        for i in range(0, self.settings.getProperty('numIterations')):

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
            self.policyLearner.updateModel_fromData(fullData)

            # store some basic values
            self.store('avgReturns', np.mean(newData.getDataEntry('returns')), TrialStoringType.ACCUMULATE)
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


if __name__ == "__main__":
    script = PowerRosenbrock('/tmp/testCategory/PowerRosenbrock', 0);
    script.configure();
    script.run();