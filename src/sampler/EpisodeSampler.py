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
