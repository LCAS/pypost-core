from pypost.sampler.initialSampler.InitialStateSampler import InitialStateSampler
import numpy as np
import warnings

class InitialStateSamplerStandard(InitialStateSampler):

    def __init__(self, dataSampler):

        super().__init__(dataSampler)

        self.initialStateDistributionMinRange = -1
        self.initialStateDistributionMaxRange =  1
        self.initialStateDistributionType = 'Gaussian'

        self.linkProperty('initialStateDistributionMinRange')
        self.linkProperty('initialStateDistributionMaxRange')
        self.linkProperty('initialStateDistributionType')

    def sampleInitState(self, numElements, *args):
        numDimTaken = 0
        dimState = self.dataManager.getNumDimensions('states')
        states = np.zeros((numElements, dimState))

        if all(args) == None:
            context = args[0]
            numDimTaken = np.minimum(np.shape(states)[1], np.shape(context)[1])
            states[:, 0: numDimTaken] = context[:, 1:numDimTaken]

        minRange = self.initialStateDistributionMinRange
        maxRange = self.initialStateDistributionMaxRange

        if np.isscalar(minRange) or len(minRange) == 1:
            minRange = np.ones((1, dimState)) * minRange
            maxRange = np.ones((1, dimState)) * maxRange
        #Todo see if works
        minRange = minRange[numDimTaken:]
        maxRange = maxRange[numDimTaken:]

        if self.initialStateDistributionType == 'Uniform':
            randValues = np.random.uniform(size=[numElements, dimState - numDimTaken])
            offset = minRange
            width = maxRange - minRange

        else:
            if self.initialStateDistributionType != 'Gaussian':
                warnings.warn("Unknown distribution type: " + self.initialStateDistributionType)
            randValues = np.random.normal(size=[numElements, dimState - numDimTaken])
            offset = (maxRange + minRange) / 2
            width = (maxRange - minRange) / 2
        res = randValues * width + offset
        return res