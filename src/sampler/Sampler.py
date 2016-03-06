from interfaces.SamplerInterface import SamplerInterface


class Sampler(SamplerInterface):
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
        super().__init__()

        self.dataManager = dataManager
        '''
        The data manager responsible for this sampler
        '''
        self._samplerName = samplerName
        '''
        String of the sampler name
        :change: now holds samplerPool instances instead of their names
        '''
        self._samplerPools = {}
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
        self._iterationIndex = 0
        '''
        Index of the current iteration
        '''
        self._lowerLevelSamplers = []
        '''
        List of lower level samplers
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

    def setSamplerIteration(self, iteration):
        '''
        Set the iteration index
        '''
        self._iterationIndex = iteration

    # FIXME see parent class comment
    def appendNewSamples(self):
        '''
        Sets the append attribute to true
        '''
        return True

    def finalizeSampler(self, finalizeData):
        '''
        Finalize the samplerMap and the data
        :param finalizeData: Set to true if the dataManager should finalize the data
        :change: finalizeData is no longer optional
        '''
        lowLevelsamplers = self.getLowLevelSamplers()
        for sampler in lowLevelsamplers:
            if sampler in self._samplerMap:
                raise RuntimeError(
                    "Added already added lower-level sampler \"" + sampler.getSamplerName() + "\"")
            sampler.finalizeSampler(False)
            self._samplerMap[sampler.getSamplerName()] = sampler

        if finalizeData:
            self.dataManager.finalizeDataManager()

    def copyPoolsFromSampler(self, sampler):
        '''
        Clears this sampler and copies all sampler pools and their corresponding priority
        :param sampler: sampler to copy the sampler pools from
        '''
        self._samplerPools = sampler._samplerPools.copy()
        self._samplerPoolPriorityList = sampler._samplerPoolPriorityList.copy()
        # ASK the line below was commented out in matlab code is there a reason for that? ^mw
        # self._lowerLevelSamplers=sampler.lowerLevelSamplers
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

    def isSamplerFunction(self, samplerName):
        '''
        Checks if a sampler function is part of this sampler
        :param samplerName: name of the sampler function to test
        :returns: true if the sampler is a sampler function of this sampler; false otherwise
        '''
        if self.getSamplerName() == samplerName:
            return True
        else:
            return super().isSamplerFunction(samplerName)

    def callDataFunction(self, samplerName, newData, *args):
        '''
        Calls a data function on a given sampler
        :param samplerName: sampler to call the function on
        :param newData: data to pass to the function
        :param args: further parameters to pass
        '''
        if self.getSamplerName() == samplerName:
            self._createSamples(newData, *args)
        else:
            super().callDataFunction(samplerName, newData, *args)

    def addSamplerPool(self, samplerPool):
        '''
        Adds a sampler pool to the sampler pool list

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
        index = 0
        for idx, pool in enumerate(self._samplerPoolPriorityList):
            if samplerPool.getPriority() == pool.getPriority():
                raise RuntimeError(
                    "A sampler pool with the same priority already exists")

            if samplerPool.getPriority() > pool.getPriority():
                index = idx
                break

        self._samplerPoolPriorityList.insert(index, samplerPool)

    def getSamplerPool(self, name):
        '''
        Get a reference to a sampler pool
        :param name: Name of the sampler pool
        :returns: requested pool
        :raises: NameError: if no pool is registered under the given name
        '''
        return self._samplerPools[name]

    # CHANGE flushSamplerPool got deleted. Call getSamplerPool(name).flush()

    def addLowerLevelSampler(
            self, samplerPool, lowerLevelSampler, isBeginning):
        '''
        Adds a lower-level sampler to this sampler
        :param samplerPool: name of the sampler pool
        :param lowerLevelSampler: sampler to add to the pool
        :param isBeginning: ASK what is this doing?
        #ASK where is addSamplerFunction defined,
        '''
        self.addSamplerFunction(samplerPool, lowerLevelSampler, isBeginning)
        self._lowerLevelSamplers.append(lowerLevelSampler)

    # ASK unify names as low- or lowerLevelSamplers?
    def getLowerLevelSamplers(self):
        '''
        Get a list of all recursively invoked lower-level samplers
        :returns: list of all lower-level samplers
        '''

        lowerLevelSamplersRecursive = self._lowerLevelSamplers.copy()
        # we iterate breadth-first by adding new lower-level iterators to the
        # end of the list
        for sampler in self._lowerLevelSamplers:
            lowerLevelSamplersRecursive.extend(sampler.getLowerLevelSamplers())

        return lowerLevelSamplersRecursive

    def addSamplerFunctionToPool(
            self, samplerPoolName, samplerName, objHandle, addLocationFlag=1):
        '''
        #FIXME this function does multiple things a once. bad design?
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
        if not self.isSamplerFunction(samplerName):
            raise RuntimeError(
                samplerName + " is not a valid sampler function of the object")

        # ASK sampleFunction was never as an object in Matlab, is this the
        # default behaviour?
        sampleFunction = {}
        sampleFunction.samplerName = samplerName
        sampleFunction.objHandle = objHandle

        pool = self._samplerPools[samplerPoolName]

        def case0(self):
            pool.samplerList.insert(0, sampleFunction)

        def case1(self):
            pool.clear()
            pool.append()

        def case2(self):
            pool.append()
        switch = {
            0: case0,
            1: case1,
            2: case2
        }
        switch[addLocationFlag](self)

    def createSamplesFromPool(self, pool, data, *args):
        '''
        Executes all functions on the samplerList of a given pool

        :param poolName: name of the selected pool
        :param data: the data structure the pool operates on
        :param args: hierarchical indexing of the data structure
        '''
        for sampler in pool.samplerList:
            objectPointer = sampler.objHandle
            objectPointer.callDataFunction(sampler.getName(), data, *args)

    def sampleAllPools(self, data, *args):
        '''
        Sample all pools

        :param newData: the data structure the pool operates on
        :param *args: hierarchical indexing of the data structure
        '''
        for pool in self._samplerPoolPriorityList:
            self.createSamplesFromPool(pool, data, *args)

    def createSamplesFromPoolWithPriority(
            self, lowPriority, highPriority, data, *args):
        '''
        Samples all pools in a specific priority range

        :param lowPriority: lower bound of pools that will be executed
        :param highPriority: higher bound of pools that will be executed
        :param newData: the data structure the pool operates on
        :param *args: hierarchical indexing of the data structure
        '''
        for pool in self._samplerPoolPriorityList:
            if pool.getPriority() >= lowPriority:
                # break if we exceed to upper bound
                if pool.getPriority() > highPriority:
                    break
                self.createSamplesFromPool(pool, data, *args)

    # change _addSamplerToPoolInternal was deleted because it can be replaced by
    # addSamplerFunctionToPool with addLoctionFlag 0

    # ASK addSamplerFunction referenced in MatLab code does not exists
    # CHANGE removed _addSamplerToPoolInternal
