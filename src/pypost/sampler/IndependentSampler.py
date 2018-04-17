from pypost.sampler.Sampler import Sampler


class IndependentSampler(Sampler):
    '''
    Methods (annotated):
    def __init__(self, dataManager: data.DataManager, samplerName: str) -> null
    def setParallelSampling(self, parallelSampling: Boolean) -> null
    def getParallelSampling(self) -> Boolean
    def createSamples(self, newData: data.Data, numElements: int = None) -> null
    '''

    def __init__(self, dataManager, samplerName, numSamples = 10):
        '''
        Constructor

        :param dataManager: DataManager this sampler operates on
        :param samplerName: Name of this sampler
        :param numSamples: The number of samples to use for after the initial iteration
        :
        '''
        Sampler.__init__(self, dataManager, samplerName)

        self._parallelSampling = True
        '''
        Determines if the episodes are sampled parallel or in sequentially
        '''

        self.numSamples = numSamples
        '''
        The number of samples to use for after the initial iteration
        '''

        self._numInitialSamples = -1
        self.iterationNumber = 0
        '''
        The number of samples to use for for the initial iteration
        '''

        # :change:
        # ASK im Matlab the sampler name was converted into upper case. Is this
        # important? (Dont "correct" user errors!)
        self.dataManager.addDataEntry('iterationNumber', 1)

        self.linkPropertyToSettings('numSamples', globalName = 'numSamples' + samplerName.capitalize())
        self.linkPropertyToSettings("_numInitialSamples", globalName = "numInitialSamples" + samplerName.capitalize())


    def setParallelSampling(self, parallelSampling):
        '''
        When set True, the episodes are sampled parallel; otherwise: sequentially
        '''
        self._parallelSampling = parallelSampling

    def getParallelSampling(self):
        '''
        Returns True, if the episodes are sampled parallel; False, if they are sampled sequentially
        '''
        return self._parallelSampling

    def createSamples(self, newData):
        '''
        Creates the samples from the given Data.

        :param newData: the data structure the sampler operates on
        :param numElements: Not implemented yet
        '''

        indices = newData.activeIndex

        numSamples = self.getNumSamples(newData)
        if not isinstance(numSamples, list):
            numSamples = [numSamples]
        if isinstance(indices, tuple):
            indices = list(indices)

        if (len(indices) > self.samplerDepth + 1 or len(indices) < self.samplerDepth):
            raise ValueError('Invalid Index for sampler. Hierarchical Index must not be larger than {0} and smaller than {0}'.format(self.samplerDepth + 1, self.samplerDepth))


        if (len(indices) == self.samplerDepth):
            indices.append(slice(0, numSamples[0]))
        newIndices = indices.copy()

        if all(numSamples) > 0:
            newData.reserveStorage(numSamples, indices[1:])
            newData.setDataEntry('iterationNumber', ..., self.iterationNumber)

            if self.getParallelSampling():
                self.sampleAllPools(newData, newIndices)
            else:
                if isinstance(indices[self.samplerDepth], int):
                    self.sampleAllPools(newData, newIndices)
                else:
                    if isinstance(indices[self.samplerDepth], slice):
                        listIndices = list(range(indices[self.samplerDepth].start, indices[self.samplerDepth].stop))
                    elif indices[self.samplerDepth] == Ellipsis:
                        listIndices = list(range(numSamples[self.samplerDepth]))
                    else:
                        # must be int list then...
                        listIndices = indices[self.samplerDepth]
                    index = 0
                    while index < len(listIndices):
                        newIndices[self.samplerDepth] = listIndices[index]
                        self.sampleAllPools(newData, newIndices)
                        if self.isValidEpisode():
                            index = index + 1

        self.iterationNumber += 1

    def isValidEpisode(self):
        '''
        Returns True, if this is a valid episode (which is the case)
        '''
        return True

    def getNumSamples(self, data):
        '''
        Returns number of samples to use for the current iteration
        '''
        if self.iterationNumber == 0 and self._numInitialSamples > 0:
            numSamples = self._numInitialSamples
        else:
            numSamples = self.numSamples

        return numSamples
