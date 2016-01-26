'''
Created on 26.01.2016

@author: Moritz
'''
from sampler import IndependentSampler
from data import DataManager
from sampler import SamplerPool


class EpisodeSampler(IndependentSampler):
    '''
    Sets up an sampler for episodes
    '''

    def __init__(self, dataManager=None, samplerName=None):
        '''
        @param dataManager: DataManager this sampler operates on
        @param samplerName: name of this sampler
        '''
        if samplerName is None:
            samplerName = "episodes"

        if dataManager is None:
            dataManager = DataManager(samplerName)

        super().__init__(dataManager, samplerName)

        self.contextDistribution = None
        self.returnSampler = None
        self.parameterPolicy = None

        self.addDataAlias("contexts", {})
        self.addSamplerPool(SamplerPool("InitEpisode", 1))
        self.addSamplerPool(SamplerPool("ParameterPolicy", 3))
        self.addSamplerPool(SamplerPool("Episodes", 5))
        self.addSamplerPool(SamplerPool("FinalReward", 6))
        self.addSamplerPool(SamplerPool("Return", 7))

    def getEpisodeDataManager(self):
        return self.dataManager

    def setFinalRewardSampler(self, rewardSampler, samplerName=None):
        '''
        @param rewardSampler: sampler function to set
        @param samplerName: name of the sampler function
        #TODO require explicit sampler
        '''
        if samplerName is None:
            samplerName = "sampleReturn"

        # FIXME add extra argument and do not rely on sampler name
        if samplerName == "sampleReturn":
            self.returnSampler = rewardSampler

        self.addSamplerFunctionToPool("Return", samplerName, rewardSampler, -1)

    def setParameterPolicy(self, parameterSampler, samplerName=None):
        '''
        @param parameterSampler: sampler function to set
        @param samplerName: name of the sampler function
        #TODO require explicit sampler
        '''
        if samplerName is None:
            samplerName = "sampleParameter"

        # FIXME add extra argument and do not rely on sampler name
        if samplerName == "sampleParameter":
            self.parameterPolicy = parameterSampler

        self.addSamplerFunctionToPool(
            "ParameterPolicy", samplerName, parameterSampler, -1)

    def setContextsampler(self, contextSampler, samplerName=None):
        '''
        @param contextSampler: sampler function to set
        @param samplerName: name of the sampler function
        #TODO require explicit sampler
        '''
        if samplerName is None:
            samplerName = "sampleContext"

        # FIXME add extra argument and do not rely on sampler name
        if samplerName == "sampleContext":
            self.contextDistribution = contextSampler

        self.addSamplerFunctionToPool(
            "InitEpisode", samplerName, contextSampler, -1)

    def flushReturnFunction(self):
        self.getSamplerPool("Return").flush()

    def flushFinalRewardFunction(self):
        self.getSamplerPool("FinalReward").flush()

    def flushParameterPolicy(self):
        self.getSamplerPool("ParameterPolicy").flush()

    def flushContextSampler(self):
        self.getSamplerPool("InitEpisode").flush()
