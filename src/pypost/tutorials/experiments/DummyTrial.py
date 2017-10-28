import numpy as np

from pypost.experiments.Trial import TrialStoringType
from pypost.experiments.Trial import Trial

from pypost.mappings.GaussianLinearInFeatures import GaussianLinearInFeatures
from pypost.supervisedLearner.LinearGaussianMLLearner import LinearGaussianMLLearner
from pypost.banditEnvironments.RosenbrockReward import RosenbrockReward

from pypost.sampler.EpisodeSampler import  EpisodeSampler

class DummyTrial(Trial):

    def __init__(self, evalDir, trialIndex, trialSettings = None):
        super(DummyTrial, self).__init__(evalDir, trialIndex, trialSettings)

    def _configure(self):
        # set some basic parameters

        self.settings.setProperty("temperature", 1)
        self.settings.setProperty("numEpisodes", 10)
        self.settings.setProperty("numIterations", 500)

        # Apply external settings

        self.applyTrialSettings()

        # create the sampler
        self.sampler = EpisodeSampler()
        self.dataManager = self.sampler.dataManager

        # add the reward function
        self.returnSampler = RosenbrockReward(
            self.dataManager,
            numContexts = 0,
            numParameters = 10)

        # set the parameter policy
        self.parameterPolicy = GaussianLinearInFeatures(self.dataManager, inputVariables=['contexts'], outputVariables=['parameters'], name = 'parameterPolicy')
        self.dataManager.addDataEntry('returnWeighting', 1)
        self.policyLearner = LinearGaussianMLLearner(self.dataManager, self.parameterPolicy, 'returnWeighting')

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
        newData = self.dataManager.createDataObject(self.settings.numEpisodes)

        # do all iterations
        for i in range(0, self.settings.getProperty('numIterations')):

            self.nextIteration()

            # create new samples
            self.sampler >> newData

            # get return vector
            returns = newData[...].returns

            maxR = np.max(returns)
            minR = np.min(returns)
            returns = returns - maxR
            returns = returns / (maxR - minR)

            #compute weights
            weights = np.exp(returns / self.settings.temperature)

            #register weights in data
            newData[...].returnWeighting = weights


            # update the model in order to actually learn something
            newData >> self.policyLearner

            # store some basic values
            self.store('avgReturns', np.mean(newData.getDataEntry('returns')))

            # print some information about the current progress
            print(
                "Iteration: %d, Episodes: %d, AvgReturn: %f" %
                (i, i * self.settings.getProperty('numSamplesEpisodes'),
                 np.mean(newData.getDataEntry('returns'))))


if __name__ == "__main__":
    script = DummyTrial('/tmp/testCategory/Tutorial', 0);
    script.configure();
    script.run();