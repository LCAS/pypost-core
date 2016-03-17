from functions.MappingInterface import MappingInterface


class ParametricFunction(MappingInterface):

    def ParametricFunction():
        MappingInterface()

    def registerGradientFunction(self):
        if self.inputVariables is None or not isinstance(
           self.inputVariables[0], np.ndarray):
            self.addDataManipulationFunction('getGradient',
                                             self.inputVariables,
                                             [self.outputVariable, 'Grad'])

    def registerGradientDataEntry(self):
        self.dataManager.addDataEntry([self.outpurVariable, 'Grad'],
                                      self.numParameters);

    def getGradient(self, varargin):
        raise NotImplementedError()

    def getNumParameters(self):
        raise NotImplementedError()

    def setParameterVector(self, theta):
        # TODO: matlab code does not make sense
        return getParameterVector(self)
