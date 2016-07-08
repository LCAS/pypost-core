import warnings
from scipy.optimize import minimize
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

class SciPyBasedUnconstrained(Unconstrained):

    def __init__(self, numParams, optimizationName=''):
        super().__init__(numParams, optimizationName)

        self.method = 'Nelder-Mead'
        self.epsilon = 1e-6

        self.linkProperty('method', optimizationName + 'method')
        self.linkProperty('epsilon', optimizationName + 'epsilon')

        # Suppress warnings of optimizer about unknown (and hence ignored) options
        if not self.verbose:
            warnings.filterwarnings('ignore', '.*Unknown solver options:*.')

    def _optimize_internal(self, **kwargs):
        if self.verbose:
            print('Starting Optimization with', self.method)

        if kwargs:
            opt_dict = kwargs
        else:
            opt_dict = dict()

        opt_dict['disp'] = self.verbose
        opt_dict['maxiter'] = self.maxNumOptiIterations
        opt_dict['xtol'] = self.optiAbsxTol
        opt_dict['ftol'] = self.optiAbsfTol
        opt_dict['epsilon'] = self.epsilon

        result = minimize(self.function, self.x0, method=self.method, jac=self.jacobian, hess=self.hessian, options=opt_dict)

        return result.x, result.fun, result.nit