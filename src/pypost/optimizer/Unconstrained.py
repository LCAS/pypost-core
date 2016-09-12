from pypost.common.SettingsClient import SettingsClient
import numpy as np
import abc
from pypost.common import SettingsManager

class Unconstrained(SettingsClient):

    def __init__(self, numParams, optimizationName=''):
        super().__init__()

        self.optimizationName = optimizationName
        self.numParams = numParams

        self.maxNumOptiIterations = 100
        self.maxNumOptiEvaluations = 100
        self.verbose = False
        self.optiStopVal = []
        self.optiAbsfTol = 1e-12
        self.optiAbsxTol = 1e-12
        self.optiAbsgTol = 1e-12
        self.optiMaxTime = 5 * 60 * 60  # in seconds!
        # for gradient approximation
        self.epsilon = 1e-6

        self.linkProperty('maxNumOptiIterations', optimizationName + 'maxNumIterations')
        self.linkProperty('maxNumOptiEvaluations', optimizationName + 'maxNumEvaluations')
        self.linkProperty('optiStopVal', optimizationName + 'OptiStopVal')
        self.linkProperty('optiAbsfTol', optimizationName + 'OptiAbsfTol')
        self.linkProperty('optiAbsxTol', optimizationName + 'OptiAbsxTol')
        self.linkProperty('optiAbsgTol', optimizationName + 'OptiAbsgTol')
        self.linkProperty('optiMaxTime', optimizationName + 'OptiMaxTime')
        self.linkProperty('epsilon', optimizationName + 'epsilon')

        self.isMaximize = False
        self.expParameterTransform = np.zeros((numParams,), dtype=bool)

    #def _transformParameters(self, parameters):
    def _fromLogSpace(self, parameters):
        parameters[self.expParameterTransform] = np.exp(parameters[self.expParameterTransform])
        return parameters


    #def _unTransformParameters(self, parameters):
    def _toLogSpace(self, parameters):
        parameters[self.expParameterTransform] = np.log(parameters[self.expParameterTransform])
        return parameters




    def _transformObjectiveFunction(self):
        orig_func = self.function
        self.function = lambda x: orig_func(self._toLogSpace(x))
        if self.gradient is not None and not isinstance(self.gradient, bool):
            orig_grad = self.gradient
            self.gradient = lambda x: orig_grad(self._toLogSpace(x))
        if self.hessian is not None:
            orig_hess = self.hessian
            self.hessian = lambda x: orig_hess(self._toLogSpace(x))


    def _invertObjectiveFunction(self):
        if isinstance(self.gradient, bool) and self.gradient is True:
            orig_func = self.function
            def _funcAndGradInv(x):
                f, fd = orig_func(x)
                return -f, -fd
            self.function = _funcAndGradInv

        else:
            orig_func = self.function
            self.function = lambda x: - orig_func(x)
            if self.gradient is not None:
                orig_grad = self.gradient
                self.gradient = lambda x: - orig_grad(x)
            if self.hessian is not None:
                orig_hess = self.hessian
                self.hessian = lambda x: - orig_hess(x)


    # Todo check if transform parameters done right and what it is for
    def optimize(self, func, gradient=None, hessian=None, x0=None, **kwargs):

        self.function = func
        self.gradient = gradient
        self.hessian = hessian

        if self.isMaximize:
            self._invertObjectiveFunction()

        transform_parameters = any(self.expParameterTransform)
        if transform_parameters:
            self._transformObjectiveFunction()
        if x0 is None:
            self.x0 = np.zeros(self.numParams)
        else:
            self.x0 = x0
        if self.verbose:
            self.printProperties()
        
        optimal_params, optimal_value, iterations = self._optimize_internal(**kwargs)
        if transform_parameters:
            optimal_params = self._fromLogSpace(optimal_params)
        return optimal_params, optimal_value, iterations
            


    @abc.abstractmethod
    def _optimize_internal(self, **kwargs):
        return




