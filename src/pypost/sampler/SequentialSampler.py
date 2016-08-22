from pypost.sampler.Sampler import Sampler
from pypost.data.DataManipulator import DataManipulator
from pypost.sampler.isActiveSampler.IsActiveNumSteps import IsActiveNumSteps
import numpy as np

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

    def __init__(self, dataManager, samplerName, stepName, isActiveSampler = None):
        '''
        Constructor for setting-up an empty step sampler
        :param dataManager: DataManager this sampler operates on
        :param samplerName: name of this sampler
        :param stepName: name of the steps
        '''
        super().__init__(dataManager, samplerName)

        if (isActiveSampler == None):
            self._isActiveSampler = None

            # TODO pass an other IsActiveStepSampler by parameters
            self.setIsActiveSampler(IsActiveNumSteps(dataManager, stepName))
        else:
            self._isActiveSampler = isActiveSampler

    #getter & setter

    def setIsActiveSampler(self, sampler):
        self._isActiveSampler = sampler

    def createSamples(self, data):
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

        activeIndex = data.activeIndex

        if not isinstance(activeIndex, list):
            activeIndex = [activeIndex]

        for i in range(0, len(activeIndex)):
            if (isinstance(activeIndex[i], slice)):
                activeIndex[i] = list(range(activeIndex[i].start, activeIndex[i].stop))
            if (activeIndex[i] == Ellipsis):
                if (i == 0):
                    activeIndex[i] = list(range(0, data.getNumElementsForDepth(i)))
                else:
                    activeIndex[i] = list(range(0, data.getNumElementsForDepth(i) / data.getNumElementsForDepth(i - 1)))
        reservedStorage = self._isActiveSampler.toReserve()
        data.reserveStorage(reservedStorage, activeIndex)

        activeIndex.append(0)

        self._initSamples(data, activeIndex.copy())

        step = 0
        finished = False
        numSteps = self.getNumSamples(data, activeIndex)
        while(not finished):

            activeIndex[-1] = step
            # TODO activeIndex
            self._createSamplesForStep(data, activeIndex[:])

            step = step + 1

            activeIndexNew, finished = self.selectActiveIdxs(data, activeIndex)

            # TODO speed up by merging all&map
            if (step > reservedStorage and not finished):
                reservedStorage = reservedStorage * 2
                numSteps[0] = reservedStorage

                data.reserveStorage(numSteps, activeIndexNew[:-1])

            activeIndex = activeIndexNew

            if (not finished):
                self._endTransition(data, activeIndex)

    def getNumSamples(self, data, *args):
        # @mw ASK: Mistake in Matlab code? Parameters not used.
        return self._isActiveSampler.toReserve()

    def selectActiveIdxs(self, data, activeIndex):
        '''
        assumes args is a vector
        '''
        isActive = data[activeIndex] > self._isActiveSampler.isActiveStep  # @mw ASK: *args?
        tCurrent = activeIndex[-1]


        finished = not any(isActive)
        # resolve active indices if we have multple layers...
        if len(activeIndex) > 2:
            if len(activeIndex[0]) > 1:
                activeIndexTmp = [activeIndex[0][i] for i, x in enumerate(isActive) if x]
                stoppedIdxsTmp = [activeIndex[0][i] for i, x in enumerate(isActive) if not x]

                activeIdxs = [activeIndexTmp, activeIndex[1]]
                stoppedIdxs = [stoppedIdxsTmp, activeIndex[1]]
            else:
                activeIndexTmp = [activeIndex[1][i] for i, x in enumerate(isActive) if x]
                stoppedIdxsTmp = [activeIndex[1][i] for i, x in enumerate(isActive) if not x]

                activeIdxs = [activeIndex[0], activeIndexTmp]
                stoppedIdxs = [activeIndex[0], stoppedIdxsTmp]
        else:
            activeIdxs = [[activeIndex[0][i] for i, x in enumerate(isActive) if x]]
            stoppedIdxs = [[activeIndex[0][i] for i, x in enumerate(isActive) if not x]]

        if len(stoppedIdxs[0]) > 0:
            data.reserveStorage(tCurrent + 1, stoppedIdxs)

        activeIdxs.append(tCurrent)

        return (activeIdxs, finished)


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

    def _endTransition(self, data, *args):
        pass