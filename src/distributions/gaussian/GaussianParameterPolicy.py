from distributions.gaussian.GaussianLinearInFeatures import \
GaussianLinearInFeatures


class GaussianParameterPolicy(GaussianLinearInFeatures):
    def __init__(self, dataManager, outputVar='parameters', inputVar='contexts',
                 policyName='GaussianParameter'):
        '''
        Constructor
        '''
        GaussianLinearInFeatures.__init__(self, dataManager, outputVar, inputVar, policyName)

        # TODO: move addDataManipulationFunction somewhere else?
        self.addDataManipulationFunction(self.sampleFromDistribution, inputVar,
                                         outputVar)
        self.addDataFunctionAlias('sampleParameter', 'sampleFromDistribution')
