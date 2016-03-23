import numpy as np
from functions.MappingInterface import MappingInterface


class ParametricFunction(MappingInterface):

    def __init__(self):
        MappingInterface.__init__(self)

    def registerGradientFunction(self):
        if self.inputVariables is None or not isinstance(
           self.inputVariables[0], np.ndarray):
            self.addDataManipulationFunction(self.getGradient,
                                             self.inputVariables,
                                             [self.outputVariable[0] + 'Grad'])

    def registerGradientDataEntry(self):
        self.dataManager.addDataEntry(self.outputVariable + 'Grad',
                                      self.numParameters);

    def getGradient(self, *args):
        raise NotImplementedError()

    def getNumParameters(self):
        raise NotImplementedError()

    def setParameterVector(self, theta):
        raise NotImplementedError()
