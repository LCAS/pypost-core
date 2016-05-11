from pypost.distributions.gaussian.GaussianLinearInFeatures import \
GaussianLinearInFeatures


class GaussianParameterPolicy(GaussianLinearInFeatures):
    def __init__(self, dataManager, outputVar=None, inputVar=None,
                 policyName='GaussianParameter'):
        '''
        Constructor
        '''
        if inputVar is None: #pragma nobranch
            outputVar = 'parameters'
            inputVar = ['contexts']

        GaussianLinearInFeatures.__init__(self, dataManager, outputVar, inputVar, policyName)

        self.addDataFunctionAlias('sampleParameter', 'sampleFromDistribution')
