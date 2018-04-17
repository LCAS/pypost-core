from pypost.mappings.Mapping import Mapping
import tensorflow as tf

class Sampler(Mapping):
    '''
    Sampler serves as a base class for all other samplers. But you should
    consider using the subclasses SequentialSampler, IndependentSampler or for
    a learning scenario EpisodeSampler or EpisodeWithStepSampler.

    Every sampler models a sampling scenario. Various sampler pools will be
    used to handle action policy, simulating the environment, rewards and
    such. Each of those pools may contain a number of sampler functions acting
    on a given Data.Data structure. The task of the sampler is organizing
    those pools and their execution.
    '''

    # attributes

    def __init__(self, dataManager, samplerName):
        '''
        Constructor for setting-up an empty sampler

        :param dataManager: DataManager this sampler operates on
        :param samplerName: name of this sampler
        '''
        Mapping.__init__(self, dataManager, inputVariables=[], outputVariables=[])

        self._samplerPools = {}
        self._samplerName = samplerName

        if (not dataManager.getDataManagerForName(samplerName)):
            raise ValueError('Name of the sampler (%s) must be contained as a layer in the data manager' % samplerName)
        self.samplerDepth = dataManager.getLevelForDataManager(samplerName)
        '''
        Map of all sampler pools by name
        '''
        self._samplerPoolPriorityList = []
        '''
        List of all pools ordered by priority
        '''
        self._samplerMap = {}
        '''
        List of lower level samplers after finalizing the sampler
        :change: iteration indices now start at 0
        '''


    # getters & setters

    def getSamplerName(self):
        '''
        Get the sampler name
        '''
        return self._samplerName

    def _setSamplerName(self, samplerName):
        '''
        Set the sampler name
        '''
        self._samplerName = samplerName


    def copyPoolsFromSampler(self, sampler):
        '''
        Clears this sampler and copies all sampler pools and their
        corresponding priority

        :param sampler: sampler to copy the sampler pools from
        '''
        self._samplerPools = sampler._samplerPools.copy()
        self._samplerPoolPriorityList = sampler._samplerPoolPriorityList.copy()
        # ASK the line has nothing to do with sampler pools, is this still
        # correct? ^mw
        self._samplerMap = sampler._samplerMap.copy()

    def copySamplerFunctionsFromPool(self, sampler, poolName):
        '''
        Copies a sampler pool into this sampler

        :param sampler: sampler to copy the pool from
        :param poolName: sampler pool name to copy
        '''
        self._samplerPools[poolName] = sampler._samplerPools[poolName]


    def addSamplerPool(self, samplerPool):
        '''
        Adds a sampler pool to the sampler pool list

        :param samplerPool: The SamplerPool to add
        :raises: RuntimeError: If a sampler pool with the same name already
                               exists
        :raises: RuntimeError: If a sampler pool with the same priority already
                               exists
        :change: we explicitly require a sampler pool instance in case the pool class will be altered in the future
        '''
        if samplerPool.getName() in self._samplerPools.keys():
            raise RuntimeError("A sampler pool with the name \"" +
                               samplerPool.getName() + "\" already exists")

        self._samplerPools[samplerPool.getName()] = samplerPool

        # add sampler to priority list
        # assume new pool has higher priority than every pool in list. Check for lower:
        index = len(self._samplerPoolPriorityList)
        for idx, pool in enumerate(self._samplerPoolPriorityList):
            if samplerPool.getPriority() == pool.getPriority():
                raise RuntimeError(
                    "A sampler pool with the same priority already exists")
            # assumes that priority list is always ordered!
            if samplerPool.getPriority() < pool.getPriority():
                index = idx
                break

        self._samplerPoolPriorityList.insert(index, samplerPool)

    def getSamplerPool(self, name):
        '''
        Get a reference to a sampler pool

        :param name: Name of the sampler pool
        :returns: requested pool; None, if it doesn't exist
        '''
        if name in self._samplerPools.keys():
            return self._samplerPools[name]
        return None

    # CHANGE flushSamplerPool got deleted. Call getSamplerPool(name).flush()


    def addSamplerFunctionToPool(self, samplerPoolName, dataFunction, addLocationFlag=1):
        '''
        Add a function or sampler to a sampler pool

        The function behaves differently for different values of addLocationFlag
        -1 will add the new sampler function to the beginning of the sampler pool
        0 will flush the entire sampler pool and only add samplerPool afterwards
        1 will add the new sampler function at the end of the sampler pool.

        :param samplerPoolName: sampler pool to whom the sampler function will be included
        :param samplerName: name of the new sampler function
        :param objHandle: function handle of the new sampler function
        :param addLocationFlag: Determines to determines the behaviour of the
                                function.
        '''

        # ASK sampleFunction was never as an object in Matlab, is this the
        # default behaviour?
        object = None
        if (hasattr(dataFunction, '__self__')):
            object = dataFunction.__self__

        if (not hasattr(dataFunction, 'dataFunctionDecorator') and not isinstance(dataFunction, tf.Tensor)):
            raise Warning('Sampling functions need to use the DataDecorators from the DataManipulation interface')

        pool = self._samplerPools[samplerPoolName]

        if addLocationFlag == -1:
            pool.samplerList.insert(0, (object, dataFunction))
        elif addLocationFlag == 0:
            pool.samplerList.clear()
            pool.samplerList.append((object,dataFunction))
        elif addLocationFlag == 1:
            pool.samplerList.append((object, dataFunction))
        else:
            raise ValueError("Invalid value for addLocationFlag: " +
                             str(addLocationFlag))

    def sampleFromPool(self, pool, data, indices):
        '''
        Executes all functions on the samplerList of a given pool

        :param poolName: name of the selected pool
        :param data: the data structure the pool operates on
        :param indices: hierarchical indexing of the data structure
        '''
        for (object, dataFunction) in pool.samplerList:
            data[tuple(indices)] >> dataFunction >> data

    def sampleAllPools(self, data, indices):
        '''
        Sample all pools

        :param newData: the data structure the pool operates on
        :param indices: hierarchical indexing of the data structure
        '''
        for pool in self._samplerPoolPriorityList:
            self.sampleFromPool(pool, data, indices)

    def samplePoolsWithPriority(
            self, lowPriority, highPriority, data, indices):
        '''
        Samples all pools in a specific priority range

        :param lowPriority: lower bound of pools that will be executed
        :param highPriority: higher bound of pools that will be executed
        :param newData: the data structure the pool operates on
        :param indices: hierarchical indexing of the data structure
        '''
        for pool in self._samplerPoolPriorityList:
            if lowPriority <= pool.getPriority() <= highPriority:
                self.sampleFromPool(pool, data, indices)

    @Mapping.MappingMethod(inputArguments=[],outputArguments=[],takesData=True)
    def createSamples(self, data):
        pass

    # change _addSamplerToPoolInternal was deleted because it can be replaced by
    # addSamplerFunctionToPool with addLoctionFlag 0

    # ASK addSamplerFunction referenced in MatLab code does not exists
    # CHANGE removed _addSamplerToPoolInternal
