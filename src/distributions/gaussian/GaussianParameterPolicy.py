from distributions.gaussian.GaussianLinearInFeatures import \
GaussianLinearInFeatures


class GaussianParameterPolicy(GaussianLinearInFeatures):
    def __init__(self, dataManager, outputVar=None, inputVar=None,
                 policyName='GaussianParameter'):
        '''
        Constructor
        '''
        if inputVar is None:
            outputVar = 'parameters'
            inputVar = ['contexts']

        GaussianLinearInFeatures.__init__(self, dataManager, outputVar, inputVar, policyName)

        # TODO: move addDataManipulationFunction somewhere else?
        #self.addDataManipulationFunction(self.sampleFromDistribution, inputVar,
        #                                 outputVar)

        self.addDataFunctionAlias('sampleParameter', 'sampleFromDistribution')
