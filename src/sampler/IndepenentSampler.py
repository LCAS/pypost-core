'''
Created on 27.11.2015

@author: Moritz
'''
from sampler import Sampler


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

        # change
        # ASK im Matlab the sampler name was converted into upper case. is this
        # important? (dont "correct" user errors!)
        self._dataManager.addDataEntry('iterationNumber', 1)
        self._linkProperty('numSamples', ['numSamples', samplerName])
        self._linkProperty(
            "numInitialSamples", [
                "numInitialSamples", samplerName])

    def setParallelSampling(self, parallelSampling):
        self._parallelSampling = parallelSampling

    def getParallelSampling(self):
        return self._parallelSampling

    def createSamples(self, newData, *args):
        numSamples = self.getNumSamples()

        if numSamples > 0:
            newData.reserveStorage(numSamples, args[:])
            newData.resetFeatureTags()
            newData.setDataEntry('iterationNumber', self._iterationIndex)
            newIndex = args

            if self.getParallelSampling():
                newIndex.append(range(0, numSamples[1]))
                self.sampleAllPools(newData, newIndex[:])
            else:
                index = 0
                while index < numSamples[1]:
                    newIndex[args.length] = index
                    self.sampleAllPools(newData, newIndex[:])
                    if self.isValidEpisode():
                        index = index + 1

    # TODO this seems like an interface function. refactor ...
    def isValidEpisode(self):
        return True

    def getNumSamples(self, data, *args):
        if self.getNumSamples(data) == 1:
            if (self._iterationIndex == 0) and (self._numInitialSamples > 0):
                numSamples = self._numInitialSamples
            else:
                numSamples = self._numSamples
        else:
            if (self._iterationIndex == 0) and (self._numInitialSamples > 0):
                numSamples = self._numInitialSamples
            else:
                numSamples = self._numSamples[self._iterationIndex]

        return numSamples
