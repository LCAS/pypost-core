from pypost.data.DataManipulator import DataManipulator
from pypost.functions.Mapping import Mapping

import numpy as np
from pypost.common.SettingsClient import SettingsClient

class ContextualBlackBoxTask(Mapping, SettingsClient):

    def __init__(self, dataManager, dimContext, dimParameters):
        '''Constructor

        :param episodeSampler: The sampler for the lerning task
        :param dimContext: The dimensions of the context
        '''
        dataManager.addDataEntry('contexts', dimContext)
        dataManager.addDataEntry('parameters', dimParameters)
        dataManager.addDataEntry('returns', 1)

        Mapping.__init__(self, dataManager, inputVariables=['contexts','parameters'], outputVariables='returns')
        SettingsClient.__init__(self)

        self.sampleInitContextFunc = 'Gaussian'



        self.linkProperty('sampleInitContextFunc')

    @DataManipulator.DataManipulationMethod([], ['contexts'])
    def sampleFromDistribution(self, numSamples):
        if (self.dataManager.getNumDimensions('contexts') > 0):
            if (self.sampleInitContextFunc == 'Uniform'):
                return self.sampleStatesUniform(numSamples)
            elif (self.sampleInitContextFunc == 'Gaussian'):
                return self.sampleStatesGaussian(numSamples)
            else:
                raise ValueError("invalid sampleInitContextFunc")
        else:
            return np.zeros((numSamples, 0))

    def sampleStatesUniform(self, numSamples):
        minRange = self.dataManager.getMinRange('contexts')
        maxRange = self.dataManager.getMaxRange('contexts')

        states = np.random.rand(numSamples, minRange.shape[0]) *\
            np.tile(maxRange - minRange, (numSamples, 1))
        return states

    def sampleStatesGaussian(self, numSamples):
        minRange = self.dataManager.getMinRange('contexts')
        maxRange = self.dataManager.getMaxRange('contexts')

        states = np.tile((minRange + maxRange) / 2, (numSamples, 1)) +\
                 np.random.randn(numSamples, self.dimState) *\
                 np.tile((maxRange - minRange) / 2, (numSamples, 1))

        return states

    @Mapping.DataMappingFunction()
    def sampleReturn(self, *args):
        raise NotImplementedError("This method should be implemented in a " +
            "subclass.")
