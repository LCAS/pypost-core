import pypost.optimizer.scipyOptimizers.SciPyOptUtil as u
from pypost.optimizer.BoxConstrained import BoxConstrained
from scipy.optimize import minimize

class SciPyBoxConstrained(BoxConstrained):

    def __init__(self, numParams, lowerBound=None, upperBound=None, optimizationName=''):
        super().__init__(numParams, lowerBound, upperBound, optimizationName)

        self.method = 'L-BFGS-B'
        self.linkProperty('method', optimizationName + 'method')

        if not self.verbose:
            u.suppress_warnings()

    def _optimize_internal(self, **kwargs):
        if self.verbose:
            print('Starting Optimization with', self.method)



        self._adaptX0()
        bounds = self._build_bounds()
        result = minimize(self.function, self.x0, method=self.method, jac=self.jacobian, hess=self.hessian,
                          bounds=bounds, options=u.build_dict(self, kwargs))

        return result.x, result.fun, result.nit

    def _build_bounds(self):
        bounds = list()
        for lower, upper in zip(self.lowerBound, self.upperBound):
            bounds.append((lower, upper))
        return bounds
