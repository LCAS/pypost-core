from pypost.mappings.Mapping import Mapping



class BlackBoxTask(Mapping):

    def __init__(self, dataManager, dimParameters):

        dataManager.addDataEntry('parameters', dimParameters)
        dataManager.addDataEntry('returns', 1)

        super().__init__(dataManager, inputVariables='parameters', outputVariables='contexts')



    @Mapping.MappingMethod()
    def sampleReturn(self, parameters):
        raise NotImplementedError("This method should be implemented in a " +
            "subclass.")
