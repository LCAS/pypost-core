from pypost.optimizer.Unconstrained import Unconstrained
import numpy as np

class BoxConstrained(Unconstrained):

    def __init__(self, numParams, optimizerName=''):
        super().__init__(numParams, optimizerName)

    # Todo: adapt bounds by default?
    def optimize(self, func, gradient=None, hessian=None, x0=None, lowerBound=None, upperBound=None, **kwargs):
        if lowerBound is None:
            self.lowerBound = - float('inf') *  np.ones(self.numParams)
        else:
            self.lowerBound = self._toLogSpace(lowerBound)
        if upperBound is None:
            self.upperBound = float('inf') * np.ones(self.numParams)
        else:
            self.upperBound = self._toLogSpace(upperBound)
        return super().optimize(func, gradient, hessian, x0, **kwargs)

    def _adaptX0(self):
        for i, lower in enumerate(self.lowerBound):
            if self.x0[i] < lower:
                self.x0[i] = lower
        for i, upper in enumerate(self.upperBound):
            if (self.x0[i] > upper):
                self.x0[i] = upper
