from pypost.sampler.IndependentSampler import IndependentSampler
from pypost.data.DataManager import DataManager
from pypost.sampler.SamplerPool import SamplerPool


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

        self.contextDistribution = None
        self.returnSampler = None
        self.parameterPolicy = None

        self.addSamplerPool(SamplerPool("InitEpisode", 1))
        self.addSamplerPool(SamplerPool("ParameterPolicy", 3))
        self.addSamplerPool(SamplerPool("Episodes", 5))
        self.addSamplerPool(SamplerPool("FinalReward", 6))
        self.addSamplerPool(SamplerPool("Return", 7))

    def getEpisodeDataManager(self):
        return self.dataManager

    def setFinalRewardSampler(self, rewardSampler, samplerName=None, isReturnSampler=True):
        '''
        :param rewardSampler: sampler function to set
        :param samplerName: name of the sampler function
        :param isReturnSampler: set True or skip this to set the sampler as the returnSampler
        :change new parameter: isReturnSampler
        #TODO require explicit sampler
        '''
        if samplerName is None:
            samplerName = "sampleReturn"

        if isReturnSampler:
            self.returnSampler = rewardSampler

        self.addSamplerFunctionToPool("FinalReward", samplerName, rewardSampler, -1)

    def setReturnFunction(self, rewardSampler, samplerName='sampleReturn'):
        if samplerName == 'sampleReturn':
            self.returnSampler = rewardSampler

        self.addSamplerFunctionToPool('Return', samplerName, rewardSampler, -1)

    def setParameterPolicy(self, parameterSampler, samplerName=None, isParameterPolicy=True):
        '''
        :param parameterSampler: sampler function to set
        :param samplerName: name of the sampler function
        :param isParameterPolicy: set True or skip this to set the sampler as the parameterPolicy
        :change new parameter: isParameterPolicy
        #TODO require explicit sampler
        '''
        if samplerName is None:
            samplerName = "sampleParameter"

        if isParameterPolicy:
            self.parameterPolicy = parameterSampler

        self.addSamplerFunctionToPool(
            "ParameterPolicy", samplerName, parameterSampler, -1)

    def setContextSampler(self, contextSampler, samplerName=None, isContextDistribution=True):
        '''
        :param contextSampler: sampler function to set
        :param samplerName: name of the sampler function
        :param isContextDistribution: set True or skip this to set the sampler as the contextDistribution
        :change new parameter: isContextDistribution
        #TODO require explicit sampler
        '''
        if samplerName is None:
            samplerName = "sampleContext"

        if isContextDistribution:
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
