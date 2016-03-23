from data.DataManipulator import DataManipulator

import numpy as np

class EpisodicContextualLearningTask(DataManipulator):

    def __init__(self, episodeSampler, dimContext):
        '''Constructor

        :param episodeSampler: The sampler for the lerning task
        :param dimContext: The dimensions of the context
        '''
        super().__init__(episodeSampler.dataManager)

        self.dataManager = episodeSampler.dataManager
        self.sampleInitContextFunc = 0
        self.dataManager.addDataEntry('contexts', dimContext)
        self.minRangeContext = self.dataManager.getMinRange('contexts')
        self.maxRangeContext = self.dataManager.getMaxRange('contexts')

        # FIXME: the matlab implementation has both of the following statements
        self.dimContext = self.dataManager.getNumDimensions('contexts')
        self.dimContext = dimContext

        self.dataManager.addDataEntry('returns', 1)

        # FIXME self.linkProperty('sampleInitContextFunc');
        self.addDataManipulationFunction(self.sampleContext, [], ['contexts']);


    def sampleContext(self, numSamples, *args):
        if (self.dataManager.getNumDimensions('contexts') > 0):
            if (self.sampleInitContextFunc == 0):
                return self.sampleStatesUniform(numSamples)
            elif (self.sampleInitContextFunc == 1):
                return self.sampleStatesGaussian(numSamples)
            else:
                raise ValueError("invalid sampleInitContextFunc")
        else:
            return np.zeros((numSamples, 0))

    def sampleStatesUniform(self, numSamples):
        minRange = self.dataManager.getMinRange('contexts')
        maxRange = self.dataManager.getMaxRange('contexts')

        states = np.rand(numSamples, size(minRange,2)) *\
            np.tile(maxRange - minRange, (numSamples, 1))
        return states

    def sampleStatesGaussian(self, numSamples):
        minRange = self.dataManager.getMinRange('contexts')
        maxRange = self.dataManager.getMaxRange('contexts')

        states = np.tile((minRange + maxRange) / 2, (numSamples, 1)) +\
                 np.randn(numSamples, self.dimState) *\
                 np.tile((maxRange - minRange) / 2, (numSamples, 1))

        return states
