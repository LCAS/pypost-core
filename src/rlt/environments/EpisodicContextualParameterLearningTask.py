from rlt.environments.EpisodicContextualLearningTask import \
EpisodicContextualLearningTask


class EpisodicContextualParameterLearningTask(EpisodicContextualLearningTask):

    def __init__(self, episodeSampler, dimContext, dimParameters):
       super().__init__(episodeSampler, dimContext)

       self.dataManager.addDataEntry('parameters', dimParameters)
       self.dimParameters = dimParameters
       self.addDataManipulationFunction(self.sampleReturn, ['contexts', 'parameters'], ['returns'])

       self.minRangeParameters = self.dataManager.getMinRange('parameters')
       self.maxRangeParameters = self.dataManager.getMaxRange('parameters')
       self.dimParameters = self.dataManager.getNumDimensions('parameters')

    def sampleReturn(self, *args):
        raise NotImplementedError("This method should be implemented in a " +
            "subclass.")
