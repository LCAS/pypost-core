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

    def PowerRosenbrock():
        super()
        start()

    def configure(self):
        self.settings.setProperty("numContexts", 10)
        self.settings.setProperty("numParameters", 15)
        self.settings.setProperty("numSamplesEpisodes", 10)
        self.settings.setProperty("numParameters", 15)
        self.settings.setProperty("numIterations", 2000)

        self.sampler = EpisodeSampler()

        self.returnSampler = RosenbrockReward(
            self.sampler,
            self.settings.getProperty('numContexts'),
            self.settings.getProperty('numParameters'))

        self.parameterPolicy = GaussianParameterPolicy(self.dataManager)
        self.policyLearner = EpisodicPower(
            self.dataManager,
            None)

        # FIXME None should be a policyLearner instance ... is this parameter even used?
        # from the outcommented CreateFromTrial function in EpisodicPower we
        # would set trial.parameterPolicyLearner and trial.dataManager

        self.sampler.setParameterPolicy(parameterPolicy)
        self.sampler.setReturnFunction(returnSampler)

        self.configured = True

    def run(self):
        if not self.configured:
            raise RuntimeError("The trial has to be configured first.")

        newData = self.dataManager.getDataObject.getDataObject(10)

        self.parameterPolicy.initObject()

        for i in range(0, settings.getProperty('numIterations')):
            self.sampler.createSamples(newData)

            # keep old samples strategy comes here
            data = newData

            # data preprocessors come here

            self.policyLearner.updateModel(newData)

            # FIXME currently not implemented
            #trial.store("avgReturns",np.mean(newData.getDataEntry("returns")), Experiments.StoringType.ACCUMULATE)

            print(
                "Iteration: %d, Episodes: %d, AvgReturn: %f\n" %
                (i,
                 i *
                 self.settings.getProperty('numSamplesEpisodes'),
                 np.mean(
                     newData.getDataEntry('returns'))))


power_rosenbrock = PowerRosenbrock("/tmp/trial/", 0)
