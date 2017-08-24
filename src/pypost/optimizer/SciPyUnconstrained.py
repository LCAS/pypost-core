from enum import Enum

from scipy.optimize import minimize

from pypost.optimizer import SciPyOptUtil as u
from pypost.optimizer.Unconstrained import Unconstrained


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
    CG = 'CG'
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
        self.linkPropertyToSettings('method', optimizationName + 'method')

    def _optimize_internal(self, **kwargs):
        if self.verbose:
            print('Starting Optimization with', self.method)

        if (not isinstance(self.method, SciPyUnconstrainedAlgorithms)):
            raise ValueError(
                'Optimization method for constrained optimization using scipy must be of the type SciPyUnconstrainedAlgorithms')

        result = minimize(self.function, self.x0, method=self.method.value, jac=self.gradient, hess=self.hessian, options=u.build_dict(self, kwargs))

        return result.x, result.fun, result.nit

