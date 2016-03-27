from sampler import Sampler
from sampler.isActiveSampler import IsActiveNumSteps


class SequentialSampler(Sampler):
    '''
    Stages:
    - Reserving Storage specified by IsActiveSampler (Default: IsActiveNumSteps)
    - initSamples
    - createSamplesForStep and EndTransition
    - for each step for every episode check via isActiveSampler which
      of those episodes still need processing

      Methods (annotated):
      def __init__(self, dataManager: data.DataManager, samplerName: str, stepNames) -> null
      def addElementsForTransition(self, transitionElementOld: str, transitionElementNew: str) -> null
      def _setIsActiveSampler(self, sampler: sampler.isActiveSampler.IsActiveStepSampler) -> null
      createSamples(self, data: data.Data, *args: list of int) -> null
      def getNumSamples(self, data, *args) -> int
      def selectActiveIdxs(self, data: data.Data, *args: vector) -> list
      def _endTransitation(self, data: data.Data, *args: list of int) -> null
    '''

    def __init__(self, dataManager, samplerName, stepNames):
        # @mw FIXME: stepNames should rather be a string than an array!? -> comment
        '''
        Constructor for setting-up an empty step sampler
        :param dataManager: DataManager this sampler operates on
        :param samplerName: name of this sampler
        :param stepNames: array with the names of the steps
        '''
        super().__init__(dataManager, samplerName)

        self._isActiveSampler = None
        self._transitionElementOldStep = {}
        self._transitionElementNewStep = {}

        # TODO pass an other IsActiveStepSampler by parameters
        self._setIsActiveSampler(IsActiveNumSteps(dataManager, stepNames))

    #getter & setter

    def _setIsActiveSampler(self, sampler):
        self._isActiveSampler = sampler

    def addElementsForTransition(
            self, transitionElementOld, transitionElementNew):
        '''
        Adds a transition from an old to a new element name
        :param transitionElementOld: old name of the element
        :param transitionElementNew: new name of the element
        #ASK is this the place where an automatic transition for old/new-name prefixes was requested?
        '''
        self._transitionElementOldStep.append(transitionElementOld)
        self._transitionElementNewStep.append(transitionElementNew)

    def createSamples(self, data, *args):
        '''
        The sequential sampler creates samples by first initiating the data and
        after that run the appropriate sampler pools for each step and, after checking which
        episodes are still active, copy the transition elements for the new step to the next step

        It does that by initializing the dataManager via initSamples() and running createSamplesForStep and
        endTransition for each step sequentially while isActiveSampler determines which of the episodes are
        still active and need processing. If isActiveSampler returns an empty vector, meaning every episode
        has terminated, the sampling is done.

        :param data: the data structure the sampler operates on
        :param args: hierarchical indexing of the data structure
        '''

        layerIndex = args

        reservedStorage = self._isActiveSampler.toReserve()
        data.reserveStorage(reservedStorage, layerIndex.copy())

        activeIndex = layerIndex
        activeIndex.append(0)

        self._initSamples(data, activeIndex.copy())

        step = 0
        finished = False
        numSteps = self.getNumSamples(data, args)
        while(not finished):

            activeIndex[-1] = step
            # TODO activeIndex
            self.createSamplesForStep(data, activeIndex[:])

            step = step + 1
            activeIndexNew = self.selectActiveIdxs(data, activeIndex[:])

            # TODO speed up by merging all&map
            if (step > reservedStorage and all(
                    map(lambda x: x.length > 0, activeIndexNew))):
                reservedStorage = reservedStorage * 2
                numSteps[0] = reservedStorage

                data.reserveStorageNoReserveOld(numSteps, activeIndexNew[:-1])

            activeIndex = activeIndexNew

            # TODO speed up by merging any&map
            finished = any(map(lambda x: x.length == 0, activeIndex))
            if (not finished):
                self._endTransition(data, activeIndex.copy())

    def getNumSamples(self, data, *args):
        # @mw ASK: Mistake in Matlab code? Parameters not used.
        return self._isActiveSampler.toReserve()

    def selectActiveIdxs(self, data, *args):
        '''
        assumes args is a vector
        '''
        isActive = self._isActiveSampler.callDataFunctionOutput(
            'isActiveStep', data, *args) # @mw ASK: *args?
        tCurrent = args[-1]

        # ASK what is this doing?
        if args.length > 2:
            if args[0].length > 1:
                activeIdxs = [args[1:-2](isActive), args[-1], tCurrent]
                stoppedIdxs = [args[1:-2](not isActive), args[-1], tCurrent]
            else:
                activeIdxs = [args[1:-2], args[-1](isActive), tCurrent]
                stoppedIdxs = [args[1:-2], args[-1](not isActive), tCurrent]
        else:
            activeIdxs = [args[1:-1], args[-1](isActive), tCurrent]
            stoppedIdxs = [args[1:-1], args[-1](not isActive), tCurrent]

        if any(not isActive):
            data.reserveStorage(tCurrent, stoppedIdxs[1:-1])

        return activeIdxs

    def _endTransitation(self, data, *args):
        # ASK are the copies of args necessary?
        layerIndex = args.copy()
        layerIndexNew = layerIndex.copy()
        layerIndexNew = layerIndexNew[-1].copy() + 1

        for old, new in zip(
                self._transitionElementOldStep, self._transitionElementNewStep):
            elementNextTimeStep = data.getDataEntry(old, layerIndex.copy())
            # ASK this variable is set but never used
            # numElements=elementNextTimeStep.length
            data.setDataEntry(new, elementNextTimeStep, layerIndex.copy())

    def _initSamples(self, data, *args):
        '''
        Initialize the data of the step sampler
        :param data: data to be operated on
        :param args: index of the layer
        '''
        raise NotImplementedError("Not implemented")

    def _createSamplesForStep(self, data, *args):
        '''
        create samples for the current step
        :param data: to be operated on
        :param args: index of the layer
        '''
        raise NotImplementedError("Not implemented")
