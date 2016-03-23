from functions.MappingInterface import MappingInterface


class ParametricModel(MappingInterface):
    def __init__(self):
        MappingInterface.__init__(self)

    def registerGradientModelFunction(self):
        self.addDataManipulationFunction(
            self.getLikelihoodGradient,
            [self.inputVariables[:], self.outputVariable],
            [self.outputVariable[0] + 'GradLike'])

    def getFisherInformationMatrix(self):
        print('WARNING: policysearchtoolbox: Fisher Information Matrix not implemented');
        Fim = np.zeros(self.numParameters, self.numParameters)
        return Fim

    def getLikelihoodGradient(self):
        print('WARNING: policysearchtoolbox: Likelihood Gradient not implemented');
        gradient = np.zeros(self.numParameters, 1)
        return gradient
