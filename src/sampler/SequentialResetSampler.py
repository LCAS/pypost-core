from sampler.Sampler import Sampler


class SequentialResetSampler(Sampler):
    '''
    classdocs

    def __init__(self, dataManager: data.DataManager, samplerName: str) -> None
    def createSamples(self, newData: data.Data, *args: unpacked list of int) -> None
    def getNumSamples(self, data: data.Data, index) -> int
    
    '''
    # FIXME why isn't this class derived from sequential sampler?

    def __init__(self, dataManager, samplerName):
        '''
        Constructor

        :param dataManager: DataManager this sampler operates on
        :param samplerName: Name of the sampler
        '''
        super().__init__(dataManager, samplerName)

        self._numSamples = self._toReserve()
        '''
        The number of samples for this sampler.
        '''

    def createSamples(self, newData, *args):
        '''
        Creates the samples from the given Data.

        :param newData: the data structure the sampler operates on
        :param args: hierarchical indexing of the data structure
        '''

        reservedStorage = self._toReserve()
        newData.reserveStorage(reservedStorage)

        activeIndex = list(args)
        it = 1
        activeIndex.append(it)

        self._initSamples(newData, activeIndex[:])

        while(len(activeIndex[-2]) >= 1):
            if (it > reservedStorage):
                reservedStorage = reservedStorage * 2
                newData.reserveStorage(reservedStorage)

            activeIndex[-1] = it
            # last index is the number of the current iteration
            activeIndex = self._createSamplesForStep(newData, activeIndex[:])
            self._endTransition(newData, activeIndex)
            it = it + 1
        self._adjustReservedStorage(newData, activeIndex)

    def getNumSamples(self, data, index):
        '''
        Return the number of samples
        '''
        return self.numTimeSteps

    def _toReserve(self):
        '''
        Returns the storage to reserve
        '''
        raise NotImplementedError("Not implemented")

    def _endTransition(self, data, indexing):
        '''
        Ends the transition
        '''
        # FIXME this function is redefined in some other classes, refactor to
        # sampler(interface) itself?
        raise NotImplementedError("Not implemented")

    def _initSamples(self, data, indexing):
        '''
        Initialize the data of the step sampler
        :param data: data to be operated on
        :param indexing: index of the layer
        '''
        raise NotImplementedError("Not implemented")

    def _createSamplesForStep(self, data, indexing):
        '''
        create samples for the current step
        :param data: to be operated on
        :param indexing: index of the layer
        '''
        # FIXME this function is redefined in some other classes, refactor to
        # sequential sampler?
        raise NotImplementedError("Not implemented")

    def _adjustReservedStorage(self, data, indexing):
        '''
        Ends the transition
        :param data to be operated on
        :param indexing: index of the layer
        '''
        raise NotImplementedError("Not implemented")

    def _selectActiveIdxs(self, data, indexing):
        '''
        Ends the transition
        :param data: to be operated on
        :param indexing: index of the layer
        '''
        # This function is redefined in some other classes, refactor to
        # sequential sampler?
        raise NotImplementedError("Not implemented")
