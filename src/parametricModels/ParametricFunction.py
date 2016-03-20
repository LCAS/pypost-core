import numpy as np
from functions.MappingInterface import MappingInterface


class ParametricFunction(MappingInterface):

    def ParametricFunction():
        MappingInterface.__init__(self)

    def registerGradientFunction(self):
        if self.inputVariables is None or not isinstance(
           self.inputVariables[0], np.ndarray):
            self.addDataManipulationFunction(self.getGradient,
                                             self.inputVariables,
                                             [self.outputVariable[0] + 'Grad'])

    def registerGradientDataEntry(self):
        self.dataManager.addDataEntry(self.outpurVariable + 'Grad',
                                      self.numParameters);

    def getGradient(self, varargin):
        raise NotImplementedError()

    def getNumParameters(self):
        raise NotImplementedError()

    def setParameterVector(self, theta):
        # TODO: matlab code does not make sense
        return getParameterVector(self)
