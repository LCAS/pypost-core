from pypost.sampler.StepSampler import StepSampler
from pypost.sampler.EpisodeSampler import EpisodeSampler
from pypost.data.DataManager import DataManager
from pypost.data.DataManager import DataManagerTimeSeries


class EpisodeWithStepsSampler(EpisodeSampler):

    def __init__(self, dataManager=None, samplerNameEpisodes=None, samplerNameSteps=None):

        if samplerNameEpisodes is None:
            samplerNameEpisodes = 'episodes'
        if samplerNameSteps is None:
            samplerNameSteps = 'steps'

        if not dataManager:
            dataManager = DataManager(samplerNameEpisodes)
            dataManager.subDataManager = DataManagerTimeSeries(samplerNameSteps)

        super().__init__(dataManager, samplerNameEpisodes)
        self.stepSampler = StepSampler(dataManager, samplerNameSteps)
        self.dataManager.subDataManager = self.stepSampler.dataManager
        self.addSamplerFunctionToPool('Episodes', self.stepSampler.createSamples)

    def copyPoolsFromSampler(self, sampler):
        super().copyPoolsFromSampler(sampler)
        #self.flushSamplerPool('Episodes')
        self.addSamplerFunctionToPool('Episodes', self.stepSampler.createSamples())
        self.stepSampler.copyPoolsFromSampler(sampler.stepSampler)

    def setActionPolicy(self, actionPolicy):
        self.stepSampler.setPolicy(actionPolicy)

    def setInitStateSampler(self, initStateSampler):
        self.stepSampler.setInitStateSampler(initStateSampler)

    def setTransitionFunction(self, transitionFunction):
        self.stepSampler.setTransitionFunction(transitionFunction)

    def setRewardFunction(self, rewardFunction):
        self.stepSampler.setRewardFunction(rewardFunction)

    def getNumSamples(self, data, *args):
        numSamples = list()
        numSamples.append(super().getNumSamples(data, *args))
        numSamples.append(self.stepSampler.terminationFunction.toReserve())
        return numSamples

    def setTerminationFunction(self, sampler):
        self.stepSampler.setTerminationFunction(sampler)

