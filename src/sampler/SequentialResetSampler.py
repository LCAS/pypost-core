'''
Created on 26.11.2015

@author: Moritz
'''
from sampler import Sampler


class SequentialResetSampler(Sampler):
    '''
    classdocs
    '''
    # FIXME why isn't this class derived from sequential sampler?

    def __init__(self, dataManager, samplerName):
        '''
        Constructor
        '''
        super().__init__(dataManager, samplerName)

        self._numSamples = self.toReserve()
        '''
        The number of samples for this sampler
        '''

    def createSamples(self, newData, *args):
        layerIndex = args

        reservedStorage = toReserve()
        newData.reserveStorage(reservedStorage, layerIndex[:])

        activeIndex = layerIndex
        activeIndex[args.length] = 1

        self._initSamples(newData, activeIndex[:])

        it = 1
        while(activeIndex[-1].length >= 1):
            if (it > reservedStorage):
                reservedStorage = reservedStorage * 2
                newData.reservestorage(reservedStorage, activeIndex[0:-1])

            activeIndex.append(it)
            activeIndex = self._createSamplesForStep(newData, activeIndex[:])
            self._endTransition(newData, activeIndex)
            it = it + 1
        adjustReservedStorage()

    def getNumSamples(self, data, index):
        return self.numTimeSteps

    def _endTransition(self, data, *args):
        '''
        Ends the transition
        '''
        # FIXME this function is redefined in some other classes, refactor to
        # sampler(interface) itself?
        raise NotImplementedError("Not implemented")

    def _initSamples(self, data, *args):
        '''
        Initialize the data of the step sampler
        @param data: data to be operated on
        @param args: index of the layer
        '''
        raise NotImplementedError("Not implemented")

    def _createSamplesForStep(self, data, *args):
        '''
        create samples for the current step
        @param data to be operated on
        @param args: index of the layer
        '''
        # FIXME this function is redefined in some other classes, refactor to
        # sequential sampler?
        raise NotImplementedError("Not implemented")

    def _adjustReservedStorage(self, data, *args):
        '''
        Ends the transition
        @param data to be operated on
        @param args: index of the layer
        '''
        raise NotImplementedError("Not implemented")

    def _selectActiveIdxs(self, data, *args):
        '''
        Ends the transition
        @param data to be operated on
        @param args: index of the layer
        '''
        # FIXME this function is redefined in some other classes, refactor to
        # sequential sampler?
        raise NotImplementedError("Not implemented")
