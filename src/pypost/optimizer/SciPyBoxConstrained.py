from enum import Enum

from scipy.optimize import minimize

from pypost.optimizer import SciPyOptUtil as u
from pypost.optimizer.BoxConstrained import BoxConstrained

import numpy as np

class SciPyBoxConstrainedAlgorithms(Enum):
    L_BFGS_B = 'L-BFGS-B'
    TNC = 'TNC'
    SLSQP = 'SLSQP'


class SciPyBoxConstrained(BoxConstrained):

    def __init__(self, numParams, optimizationName=''):
        super().__init__(numParams, optimizationName)

        self.linkPropertyToSettings('method', defaultValue = SciPyBoxConstrainedAlgorithms.L_BFGS_B, globalName= optimizationName + 'method')
        self.result = []

    def _optimize_internal(self, **kwargs):
        if self.verbose:
            print('Starting Optimization with', self.method)

        self._adaptX0()
        bounds = self._build_bounds()

        if (not isinstance(self.method, SciPyBoxConstrainedAlgorithms)):
            raise ValueError('Optimization method for constrained optimization using scipy must be of the type SciPyConstrainedAlgorithms')

        self.result = minimize(self.function, self.x0, method=self.method.value, jac=self.gradient, hess=self.hessian,
                          bounds=bounds, options={'ftol' : self.optiAbsfTol * np.finfo(float).eps})

        return self.result.x, self.result.fun, self.result.nit

    def _build_bounds(self):
        bounds = list()
        for lower, upper in zip(self.lowerBound, self.upperBound):
            bounds.append((lower, upper))
        return bounds
