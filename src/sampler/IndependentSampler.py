import numpy as np
from sampler.Sampler import Sampler


class IndependentSampler(Sampler):
    '''
    classdocs
    '''

    def __init__(self, dataManager, samplerName):
        '''
        Constructor
        '''
        super().__init__(dataManager, samplerName)

        self._parallelSampling = True
        '''
        Determines if the episodes are samples parallel or in sequentially
        '''

        # FIXME magic number ...
        self._numSamples = 10
        '''
        The number of samples to use for after the initial iteration
        '''

        self._numInitialSamples = -1
        '''
        The number of samples to use for for the initial iteration
        '''

        # :change:
        # ASK im Matlab the sampler name was converted into upper case. Is this
        # important? (Dont "correct" user errors!)
        self.dataManager.addDataEntry('iterationNumber', 1)

        # FIXME: What is this for?
        #self._linkProperty('numSamples', ['numSamples', samplerName])
        #self._linkProperty("numInitialSamples",
        #                   ["numInitialSamples", samplerName])

    def setParallelSampling(self, parallelSampling):
        self._parallelSampling = parallelSampling

    def getParallelSampling(self):
        return self._parallelSampling

    def createSamples(self, newData, numElements=None):
        numSamples = self.getNumSamples(newData)

        if numElements is not None:
            raise NotImplementedError

        numElements = []

        if numSamples > 0:
            newData.reserveStorage(numSamples)
            # FIXME feature tags are not supported yet
            # newData.resetFeatureTags()
            newData.setDataEntry('iterationNumber', 0,
                                 np.array([self._iterationIndex]))
            newIndex = numElements

            if self.getParallelSampling():
                newIndex.append(slice(0, numSamples))
                self.sampleAllPools(newData, newIndex[:])
            else:
                index = 0
                while index < numSamples[0]:
                    newIndex[len(numElements)] = index
                    self.sampleAllPools(newData, newIndex[:])
                    if self.isValidEpisode():
                        index = index + 1

    # TODO this seems like an interface function. refactor ...
    def isValidEpisode(self):
        return True

    def getNumSamples(self, data, *args):
        if isinstance(self._numSamples, int):
            if self._iterationIndex == 0 and self._numInitialSamples > 0:
                numSamples = self._numInitialSamples
            else:
                numSamples = self._numSamples
        else:
            raise RuntimeError("Matlab code doesn't make any sense here.")
        #    if self._iterationIndex == 0 and self._numInitialSamples > 0:
        #        numSamples = self._numInitialSamples
        #    else:
        #        numSamples = self._numSamples[self._iterationIndex]

        return numSamples
