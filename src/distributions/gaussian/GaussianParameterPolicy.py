from distributions.gaussian.GaussianLinearInFeatures import \
GaussianLinearInFeatures


class GaussianParameterPolicy(GaussianLinearInFeatures):
    def __init__(self, dataManager, outputVar='parameters', inputVar='contexts',
                 policyName='GaussianParameter'):
        '''
        Constructor
        '''
        GaussianLinearInFeatures(dataManager, outputVar, inputVar, policyName)

        self.addDataFunctionAlias('sampleParameter', 'sampleFromDistribution')
