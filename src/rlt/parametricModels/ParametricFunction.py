import numpy as np
from rlt.functions.MappingInterface import MappingInterface


class ParametricFunction(MappingInterface):

    def __init__(self):
        MappingInterface.__init__(self)

    def registerGradientFunction(self):
        print(self.inputVariables)
        if self.inputVariables is None or len(self.inputVariables) == 0 or\
           not isinstance(self.inputVariables[0], np.ndarray):
            self.addDataManipulationFunction(self.getGradient,
                                             self.inputVariables,
                                             [self.outputVariables[0] + 'Grad'])

    def registerGradientDataEntry(self):
        if not isinstance(self.outputVariables, list):
            raise ValueError('self.outputVariables has to be a list')

        self.dataManager.addDataEntry(self.outputVariables[0] + 'Grad',
                                      self.numParameters);

    def getGradient(self, *args):
        raise NotImplementedError()

    def getNumParameters(self):
        raise NotImplementedError()

    def setParameterVector(self, theta):
        raise NotImplementedError()