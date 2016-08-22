from pypost.optimizer.BoxConstrained import BoxConstrained
import pypost.optimizer.nloptOptimizers.NLoptUtil as u
from pypost.optimizer.GradientEstimation import GradientEstimator

import numpy as np

import nlopt


# Only works if NLopt is properly installed
# For installation of NLopt see http://ab-initio.mit.edu/wiki/index.php/NLopt

class NLoptBoxConstrained(BoxConstrained):

    def __init__(self, numParameters, optimizationName=''):
        super().__init__(numParameters, optimizationName)

        # 0 = no limit
        self.optiMaxEval = 0
        self.method = nlopt.LD_LBFGS

        self.linkProperty('optiMaxEval', optimizationName + 'OptiMaxEval')
        self.linkProperty('method', optimizationName + 'method')


    def _optimize_internal(self, **kwargs):
        opt = nlopt.opt(self.method, self.numParams)
        self.usesGradient = u.usesGradient(opt)
        if self.verbose:
            self._printInformation(opt.get_algorithm_name())

        if self.lowerBound is not None:
            opt.set_lower_bounds(self.lowerBound)
        if self.upperBound is not None:
            opt.set_upper_bounds(self.upperBound)
        self._adaptX0()

        if len(self.optiStopVal):
            opt.set_stopval(self.optiStopVal)
        opt.set_ftol_abs(self.optiAbsfTol)
        opt.set_xtol_abs(self.optiAbsxTol)
        opt.set_maxeval(self.optiMaxEval)
        opt.set_maxtime(self.optiMaxTime)

        self._check_for_gradient()

        opt.set_min_objective(self._nl_opt_objective)
        x = opt.optimize(self.x0)
        minf = opt.last_optimum_value()
        if self.verbose:
            print(u.getReturnMessage(opt.last_optimize_result()))
        return x, minf, -1


    def _nl_opt_objective(self, x, grad):
        if self.gradient is True and self.usesGradient:
            f, fd = self.function(x)
            if grad.size > 0:
                grad[:] = fd
            return f
        else:
            if grad.size > 0:
                grad[:] = self.gradient(x)
            return self.function(x)


    def _check_for_gradient(self):
        if self.usesGradient and self.gradient is None:
            if self.verbose:
                print('No Gradient given, but needed: using finite differences with epsilon:', self.epsilon)
            gradEstimator = GradientEstimator(self.function, self.numParams, self.epsilon)
            self.gradient = gradEstimator.simpleFiniteDifferences

    def _printInformation(self, name):
        print('using:', name)
        print('ftol', self.optiAbsfTol)
        print('xtol', self.optiAbsxTol)
        print('stopval', self.optiStopVal)
        print('maximum Evaluations', self.optiMaxEval)
        print('maximum Time', self.optiMaxTime)
        if self.hessian is not None:
            print('Hessian not used by NLopt Optimizer')


