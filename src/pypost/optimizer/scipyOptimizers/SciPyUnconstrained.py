from scipy.optimize import minimize
from pypost.optimizer.Unconstrained import Unconstrained
import src.pypost.optimizer.scipyOptimizers.SciPyOptUtil as u

# Possible Methods (subset - only those for unconstrained optimization):
#   NAME         | TYPE
#   -------------+-----------------
#   Nelder-Mead  | gradient-free
#   Powell       | gradient-free
#   CG           | first order
#   BFGS         | first order
#   Newton-CG    | second order     jacobian Mandatory
#   dogleg       | trust region
#   trust-ncg    | trust region
#
# Gradients and Hessians not given are approximated

class SciPyUnconstrained(Unconstrained):

    def __init__(self, numParams, optimizationName=''):
        super().__init__(numParams, optimizationName)

        self.method = 'Nelder-Mead'
        self.linkProperty('method', optimizationName + 'method')

        # Suppress warnings of optimizer about unknown (and hence ignored) options
        if not self.verbose:
            u.suppress_warnings()

    def _optimize_internal(self, **kwargs):
        if self.verbose:
            print('Starting Optimization with', self.method)

        result = minimize(self.function, self.x0, method=self.method, jac=self.jacobian, hess=self.hessian, options=u.build_dict(self, kwargs))

        return result.x, result.fun, result.nit

