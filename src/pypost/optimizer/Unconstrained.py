from pypost.common.SettingsClient import SettingsClient
import numpy as np
import abc

class Unconstrained(SettingsClient):

    def __init__(self, numParams, optimizationName=''):
        super().__init__()

        self.optimizationName = optimizationName
        self.numParams = numParams

        self.l = round(4 + 3 * np.log(numParams)) #?
        self.maxNumOptiIterations = 100
        self.verbose = False
        self.optiStopVal = []
        self.optiAbsfTol = 1e-12
        self.optiAbsxTol = 1e-12
        self.optiMaxTime = 5 * 60 * 60  # in seconds!


        self.linkProperty('l', optimizationName + 'Lambda')
        self.linkProperty('maxNumOptiIterations', optimizationName + 'maxNumIterations')
        self.linkProperty('optiStopVal', optimizationName + 'OptiStopVal')
        self.linkProperty('optiAbsfTol', optimizationName + 'OptiAbsfTol')
        self.linkProperty('optiAbsxTol', optimizationName + 'OptiAbsxTol')
        self.linkProperty('optiMaxTime', optimizationName + 'OptiMaxTime')

        self.isMaximize = False
        self.expParameterTransform = np.zeros((numParams, 1), dtype=bool)

    def _transformParameters(self, parameters):
        parameters[self.expParameterTransform] = np.exp(parameters[self.expParameterTransform])
        return parameters

    def _unTransformParameters(self, parameters):
        parameters[self.expParameterTransform] = np.log(parameters[self.expParameterTransform])
        return parameters

    def _transformedFunction(self, x):
        intermediate = self._transformParameters(x)
        return self.originalFunction(intermediate)

    def _transformedJacobian(self, x):
        t_params = self._transformParameters(x)
        return self.originalJacobian(t_params) * t_params


    # Todo check if transform parameters done right and what it is for
    def optimize(self, func, jacobian=None, hessian=None, x0=None, **kwargs):

        if self.isMaximize:
            self.function = lambda x: -func(x)
            if jacobian:
                self.jacobian = lambda x: -jacobian(x)
            else:
                self.jacobian = None
            if hessian:
                self.hessian = lambda x: -hessian(x)
            else:
                self.hessian = None

        else:
            self.function = func
            self.jacobian = jacobian
            self.hessian = hessian
    
        transform_parameters = any(self.expParameterTransform)

        if transform_parameters:
            self.originalFunction = func
            self.function = self._transformedFunction
            self.originalJacobian = jacobian
            self.jacobian = self._transformedJacobian


        if x0 is None:
            self.x0 = np.zeros((self.numParams, 1))
        else:
            self.x0 = x0
        
        optimal_params, optimal_value, iterations = self._optimize_internal(**kwargs)
        if transform_parameters:
            optimal_params = self._unTransformParameters(optimal_params)
        return optimal_params, optimal_value, iterations
            
        
    @abc.abstractmethod
    def _optimize_internal(self, **kwargs):
        return




