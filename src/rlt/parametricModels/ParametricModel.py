from rlt.functions.MappingInterface import MappingInterface


class ParametricModel(MappingInterface):
    def __init__(self):
        MappingInterface.__init__(self)

    def registerGradientModelFunction(self):
        self.addDataManipulationFunction(
            self.getLikelihoodGradient,
            [self.inputVariables[:], self.outputVariables[0]],
            [self.outputVariables[0] + 'GradLike'])

    def getFisherInformationMatrix(self):
        raise NotImplementedError()

    def getLikelihoodGradient(self):
        raise NotImplementedError()
