from pypost.sampler.StepSampler import StepSampler
from pypost.sampler.EpisodeSampler import EpisodeSampler
from pypost.data.DataManager import DataManager

class EpisodeWithStepsSampler(EpisodeSampler):

    def __init__(self, dataManager=None, samplerNameEpisodes=None, samplerNameSteps=None):

        if samplerNameEpisodes is None:
            samplerNameEpisodes = 'episodes'
        if samplerNameSteps is None:
            samplerNameSteps = 'steps'

        super().__init__(dataManager, samplerNameEpisodes)
        self.stepSampler = StepSampler(dataManager, samplerNameSteps)
        self.dataManager.subDataManager = self.stepSampler.dataManager
        self.addSamplerFunctionToPool('Episodes', samplerNameSteps, self.stepSampler)

    def copyPoolsFromSampler(self, sampler):
        super().copyPoolsFromSampler(sampler)
        #self.flushSamplerPool('Episodes')
        self.addSamplerFunctionToPool('Episodes', self.stepSampler.samperName, self.stepSampler)
        self.stepSampler.copyPoolsFromSampler(sampler.stepSampler)

    def setActionPolicy(self, actionPolicy, samplerName=None):
        self.stepSampler.setPolicy(actionPolicy, samplerName)

    def setInitialStateSampler(self, initStateSampler, samplerName=None):
        self.stepSampler.setInitStateFunction(initStateSampler, samplerName)

    def setTransitionFunction(self, transitionFunction, samplerName=None):
        self.stepSampler.setTransitionFunction(transitionFunction, samplerName)

    def setRewardFunction(self, rewardFunction, samplerName=None):
        self.stepSampler.setRewardFunction(rewardFunction, samplerName)
        if(rewardFunction.isSamplerFunction('sampleFinalReward')):
            self.setFinalRewardSampler(rewardFunction, samplerName)

    def getNumSamples(self, data, *args):
        numSamples = list()
        numSamples.append(super().getNumSamples(data, *args))
        numSamples.append(self.stepSampler._isActiveSampler.toReserve())
        return numSamples
