import sys
import os
sys.path.insert(0, os.path.abspath("../../.."))

from experiments.Trial import Trial
from sampler.EpisodeSampler import EpisodeSampler
from common.Settings import Settings
from learner.episodicRL.EpisodicPower import EpisodicPower


class PowerRosenbrock(Trial):
    # FIXME add some infos about this class

    # trial, settingsEval = Experiment.getTrialForScript()

    def PowerRosenbrock():
        super()
        start()

    def configure(self):
        self.settings.setProperty("numParameters", 15)
        self.settings.setProperty("numContexts", 0)
        self.settings.setProperty("numSamplesEpisodes", 10)
        self.settings.setProperty("numParameters", 15)
        self.settings.setProperty("numIterations", 2000)

        self.sampler = EpisodeSampler()

        self.returnSampler = RosenbrockReward(
            self.sampler,
            self.settings.numContexts,
            self.settings.numParameters)

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

        for i in range(0, settings.numIterations - 1):
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
                 self.settings.numSamplesEpisodes,
                 np.mean(
                     newData.getDataEntry('returns'))))


power_rosenbrock = PowerRosenbrock("/tmp/trial/", 0)
