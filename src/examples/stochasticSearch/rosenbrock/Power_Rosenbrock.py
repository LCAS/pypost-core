import sys
import os
sys.path.insert(0, os.path.abspath("../../.."))

from experiments.Trial import Trial
from sampler.EpisodeSampler import EpisodeSampler
from common.Settings import Settings
from learner.episodicRL.EpisodicPower import EpisodicPower
from environments.banditEnvironments.RosenbrockReward import RosenbrockReward
from distributions.gaussian.GaussianParameterPolicy import \
GaussianParameterPolicy


class PowerRosenbrock(Trial):
    # FIXME add some infos about this class

    # trial, settingsEval = Experiment.getTrialForScript()

    # What's this?
    '''
    def PowerRosenbrock():
        super()
        start()
    '''

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

        for i in range(0, self.settings.getProperty('numIterations')):
            print('newData', newData)
            self.sampler.createSamples(newData)
            # keep old samples strategy comes here
            data = newData

            # data preprocessors come here

            self.policyLearner.updateModel(newData)

            # FIXME Test if this works
            trial.store("avgReturns",np.mean(newData.getDataEntry("returns")), Experiments.StoringType.ACCUMULATE)

            print(
                "Iteration: %d, Episodes: %d, AvgReturn: %f\n" %
                (i,
                 i *
                 self.settings.getProperty('numSamplesEpisodes'),
                 np.mean(
                     newData.getDataEntry('returns'))))


# For testing purposes. Maybe implement a better way to start trials directly?
power_rosenbrock = PowerRosenbrock("/tmp/trial/", 0)
power_rosenbrock.start()
