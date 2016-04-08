import sys
import numpy as np

sys.path.append('../../src/')

from functions.Mapping import Mapping

class MappingTestClass(Mapping):
    
    def __init__(self, dataManager):
        Mapping.__init__(self, dataManager, ['X'], 'Y', 'TestMapping')
        self.addMappingFunction(self.getFunctionValue)
        self.addMappingFunction(self.getFunctionGradient)
        
    def getFunctionValue(self, numElements, X):
        return np.sin(X)
    
    def getFunctionGradient(self, numElements, X):
        return np.cos(X)
    