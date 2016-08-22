from pypost.sampler.IndependentSampler import IndependentSampler
from pypost.data.DataManager import DataManager
from pypost.sampler.SamplerPool import SamplerPool
import types

class EpisodeSampler(IndependentSampler):
    '''
    EpisodeSampler is a subclass of IndependentSampler that allows for a
    more convenient implementation of an independent sampling.

    There are a number of SamplingPools and corresponding  access
    functions predefined. The Pools and their priority are
    defined as follows:

    - InitEpisode (Priority 1):  Sets the starting conditions for the
    episode(s). For example: a random starting position state for each episode.

    - Policy (Priority 3):  Determine the actions of the agent, usually
    depended on the actual state.

    - Episodes (Priority 5):  Run the sampler that handles each episode

    - FinalReward (Priority 6): Evaluates the result of each episode and
    returns an additional reward.

    - Return (Priority 7):  Calculates the return of each episode by
    summing the reward and the final reward
    '''

    def __init__(self, dataManager=None, samplerName=None):
        '''
        :param dataManager: DataManager this sampler operates on
        :param samplerName: name of this sampler
        '''
        if samplerName is None:
            samplerName = "episodes"

        if dataManager is None:
            dataManager = DataManager(samplerName)

        super().__init__(dataManager, samplerName)

        self.addSamplerPool(SamplerPool("InitEpisode", 1))
        self.addSamplerPool(SamplerPool("ParameterPolicy", 3))
        self.addSamplerPool(SamplerPool("Episodes", 5))
        self.addSamplerPool(SamplerPool("Return", 7))

    def getEpisodeDataManager(self):
        return self.dataManager

    def setReturnFunction(self, returnFunction):

        self.addSamplerFunctionToPool("Return", returnFunction, -1)

    def setParameterPolicy(self, parameterPolicy):
        '''
        :param parameterSampler: sampler function to set
        '''
        self.addSamplerFunctionToPool("ParameterPolicy", parameterPolicy, -1)

    def setContextSampler(self, contextSampler):
        '''
        :param contextSampler: sampler function to set
        '''
        self.addSamplerFunctionToPool("InitEpisode", contextSampler, -1)


    def flushReturnFunction(self):
        self.getSamplerPool("Return").flush()

    def flushFinalRewardFunction(self):
        self.getSamplerPool("FinalReward").flush()

    def flushParameterPolicy(self):
        self.getSamplerPool("ParameterPolicy").flush()

    def flushContextSampler(self):
        self.getSamplerPool("InitEpisode").flush()
