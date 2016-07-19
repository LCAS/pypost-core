import numpy as np
from pypost.data.DataManager import DataManager
from pypost.sampler.SequentialSampler import SequentialSampler
from pypost.sampler.SamplerPool import SamplerPool


class StepSampler(SequentialSampler):
    '''
    The StepSampler is a Sampler.SequentialSampler, hence some of his sampling pools will be called in sequential order

    After the sampler has been set up correctly, by adding the suitable functions into the sampler pools this sampler will do
    the following steps to create the samples:

    First call initSamples() which will execute the sampling pool "InitSamples" to create an initial state for the step sampler.
    Secondly, for each step, begin with calling createSamplesForStep() to execute the remaining pools (more explanation follows)
    and then after checking if any episode is terminated via isActiveSampler, transfer the data from nextStates in thr current step
    to states in the next step.

    The sampler pools in the second step, if properly configured, should do the following:
    - Policy (Priority 20): This sampler pool determines the actions of the agent within the learning process.
    - TransitionSampler (Priority 50): This pool simulates the environment, by computing the nextStates dependent on
    the states and the actions given by the policy sampler pool.
    - RewardSampler (Priority 80): This pool evaluates the reward for the sampler in each step.

    In addition to the data manipulation functions above this sampler also adds the data entries 'states', 'nextStates' and 'timeSteps'

    #FIXME step priorities are currently magic numbers ...

    Methods (annotated):
    def __init__(self, dataManager: data.DataManager, samplerName: str) -> None
    def setInitStateFunction(self, initStateSampler: sampler.Sampler, samplerName: str =None) -> None
    def setPolicy(self, policy: sampler.Sampler, samplerName: str =None) -> None
    def setTransitionFunction(self, transitionFunction: sampler.Sampler, samplerName: str =None) -> None
    def setRewardFunction(self, rewardFunction: sampler.Sampler, samplerName: str =None) -> None
    def _endTransition(self, data: data.Data, *args: unpacked list of int) -> None
    def _initSamples(self, data: data.Data, *args: unpacked list of int) -> None
    def _createSamplesForStep(self, data: data.Data, *args: unpacked list of int) -> None

    '''

    def __init__(self, dataManager, samplerName='steps'):
        '''
        Constructor for setting-up an empty step sampler
        :param dataManager: DataManager this sampler operates on
        :param samplerName: name of this sampler
        :change: sampler name is no longer optional
        :change: dataManager is no longer optional
        '''
        if dataManager is None:
            dataManager = DataManager(samplerName)
        else:
            dataManager = dataManager.getDataManagerForName(samplerName)

        super().__init__(dataManager,
                         samplerName,
                         None)

        self.addSamplerPool(SamplerPool("InitSamples", 1))
        self.addSamplerPool(SamplerPool("Policy", 20))
        self.addSamplerPool(SamplerPool("TransitionSampler", 50))
        self.addSamplerPool(SamplerPool("RewardSampler", 80))

        self.addElementsForTransition("nextStates", "states")
        self.dataManager.addDataEntry("timeSteps", 1)

    def setInitStateFunction(self, initStateSampler, samplerName=None):
        '''
        Set the initState function
        :param initStateSampler: the init state function to set
        :param samplerName: The name of the init state function (default: "sampleInitState")
        '''

        if samplerName is None:
            samplerName = "sampleInitState"

        self.addSamplerFunctionToPool(
            "InitSamples", samplerName, initStateSampler, -1)

    def setPolicy(self, policy, samplerName=None):
        '''
        Set the transition function
        :param policy: the policy function to set
        :param samplerName: The name of the sampler function (default: "sampleAction")
        '''
        if samplerName is None:
            samplerName = "sampleAction"
        self.addSamplerFunctionToPool("Policy", samplerName, policy, -1)

    def setTransitionFunction(self, transitionFunction, samplerName=None):
        '''
        Set the transition function
        :param transitionFunction: the transition function to set
        :param samplerName: The name of the sampler function (default: "samplerNextState")
        '''
        if samplerName is None:
            samplerName = "sampleNextState"
        self.addSamplerFunctionToPool(
            "TransitionSampler", samplerName, transitionFunction, -1)

    def setRewardFunction(self, rewardFunction, samplerName=None):
        '''
        Set the reward function
        :param rewardFunction: the reward function to set
        :param samplerName: The name of the reward function (default: "sampleReward")
        '''
        if samplerName is None:
            samplerName = "sampleReward"
        self.addSamplerFunctionToPool(
            "RewardSampler", samplerName, rewardFunction, -1)

    # change removed all flush functions. e.g. use
    # getSamplerPool("Policy").flush()

    def _endTransition(self, data, *args):
        '''
        End the transition and set data for the new time step
        :param data: data to be operated on
        :param args: index of the layer
        '''
        super()._endTransition(data, *args)

        # ASK see parent function
        layerIndexNew = args[0].copy()
        layerIndexNew[-1] = layerIndexNew[-1] + 1
        numElements = data.getNumElementsForIndex(len(args), *args)
        data.setDataEntry("timeSteps", layerIndexNew.copy(), np.ones(
            (numElements, 1)) * layerIndexNew[-1])

    def _initSamples(self, data, *args):
        '''
        Initialize the data of the step sampler
        :param data: data to be operated on
        :param args: index of the layer
        '''
        # the documentation states, that we set the following data entries:'states', 'nextStates' and 'timeSteps'
        # in matlab we have some lines commented out that set states &
        # timeSteps, are they still needed?
        index = args[0]
        self.createSamplesFromPool(self.getSamplerPool("InitSamples"), data, index)
        numElements = data.getNumElementsForIndex(len(args), *args)
        # time steps beginning with zero instead of one, to keep consistent with python indexing
        data.setDataEntry("timeSteps", index, np.zeros((numElements, 1)))

    def _createSamplesForStep(self, data, *args):
        '''
        sample policy, transition and reward
        :param data: to be operated on
        :param args: index of the layer
        '''
        index = args[0]
        self.createSamplesFromPoolWithPriority(10, 90, data, index)