from scipy.optimize import minimize
from pypost.optimizer.Unconstrained import Unconstrained
import src.pypost.optimizer.scipyOptimizers.SciPyOptUtil as u
from enum import Enum

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

class SciPyUnconstrainedAlgorithms(Enum):
    Nelder_Mead = 'Nelder-Mead'
    Powell = 'Powell'
    GC = 'GC'
    BFGS = 'BFGS'
    Newton_GC = 'Newton-GC'
    LBFGSB = 'L-BFGS-B'
    TNC = 'TNC'
    COBLYA = 'COBLYA'
    SLSQP = 'SLSQP'
    dogleg = 'dogleg'
    trust_ncg = 'trust-ncg'


class SciPyUnconstrained(Unconstrained):

    def __init__(self, numParams, optimizationName=''):
        super().__init__(numParams, optimizationName)

        self.method = SciPyUnconstrainedAlgorithms.Nelder_Mead
        self.linkProperty('method', optimizationName + 'method')

        # Suppress warnings of optimizer about unknown (and hence ignored) options
        if not self.verbose:
            u.suppress_warnings()

    def _optimize_internal(self, **kwargs):
        if self.verbose:
            print('Starting Optimization with', self.method)

        if (not isinstance(self.method, SciPyUnconstrainedAlgorithms)):
            raise ValueError(
                'Optimization method for constrained optimization using scipy must be of the type SciPyUnconstrainedAlgorithms')

        result = minimize(self.function, self.x0, method=self.method.value, jac=self.gradient, hess=self.hessian, options=u.build_dict(self, kwargs))

        return result.x, result.fun, result.nit

