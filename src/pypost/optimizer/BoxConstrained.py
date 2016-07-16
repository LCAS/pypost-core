from pypost.optimizer.Unconstrained import Unconstrained
import numpy as np

class BoxConstrained(Unconstrained):

    def __init__(self, numParams, lowerBound=None, upperBound=None, optimizerName=''):
        super().__init__(numParams, optimizerName)
        if lowerBound is None:
            self.lowerBound = - float('inf') *  np.ones(numParams)
        else:
            self.lowerBound = lowerBound
        if upperBound is None:
            self.upperBound = float('inf') * np.ones(numParams)
        else:
            self.upperBound = upperBound


    def getUpperBoundTransformed(self):
        return self._unTransformParameters(self.upperBound)

    def getLowerBoundTransformed(self):
        return self._unTransformParameters(self.lowerBound)

    def _adaptX0(self):
        for i, lower in enumerate(self.lowerBound):
            if self.x0[i] < lower:
                self.x0[i] = lower
        for i, upper in enumerate(self.upperBound):
            if (self.x0[i] > upper):
                self.x0[i] = upper
