from distributions.gaussian.GaussianLinearInFeatures import \
GaussianLinearInFeatures


class GaussianParameterPolicy(GaussianLinearInFeatures):
    def __init__(dataManager, outputVar='parameters', inputVar='contexts',
                 policyName='GaussianParameter'):
        '''
        Constructor
        '''
        super(dataManager, outputVar, inputVar, policyName)

        self.addDataFunctionAlias('sampleParameter', 'sampleFromDistribution')
