import cma
from pypost.optimizer.BoxConstrained import BoxConstrained
import warnings


# For this to run you need the 'cma-es' implementation installed.
# Install using pip (package is just called 'cma')
# For further information see https://www.lri.fr/~hansen/cmaesintro.html

class CMA_ES(BoxConstrained):

    def __init__(self, numParams, optimizationName=''):
        super().__init__(numParams, optimizationName)


        self.sigma0 = 1
        self.args = ()
        self.restarts = 0
        self.restartFromBest = False
        self.incpopsize=2
        self.evalInitX = None
        self.noiseHandler = None
        self.noiseChangeSigmaExponent = 1
        self.bipop = False


        self.linkProperty('args', optimizationName + 'objFuncArgs')
        self.linkProperty('restarts', optimizationName + 'nrOfRestarts')
        self.linkProperty('restartFromBest', optimizationName + 'restartFromBest')
        self.linkProperty('incpopsize', optimizationName + 'populationIncFact')
        self.linkProperty('evalInitX', optimizationName+ 'evaluateInitialX')
        self.linkProperty('noiseHandler', optimizationName + 'noiseHandler')
        self.linkProperty('noiseChangeSigmaExponent', optimizationName + 'noiseChangeSigmaExponent')
        self.linkProperty('bipop', optimizationName + 'runBIPOP-CMA-ES')

    def _optimize_internal(self, **kwargs):

        # Todo Warning and fallback?
        if isinstance(self.gradient, bool):
            self.gradient = None
            raise ValueError('CMA_ES does not support function returning gradient and function, use separate functions,'
                             'running without gradient')


        opt_dict = self._set_options(kwargs)
        self._adaptX0()

        res = cma.fmin(objective_function=self.function,
                       gradf=self.gradient, #may be none
                       x0=self.x0,
                       sigma0=self.sigma0,
                       options=opt_dict,
                       args=self.args,
                       restarts=self.restarts,
                       restart_from_best=self.restartFromBest,
                       incpopsize=self.incpopsize,
                       eval_initial_x=self.evalInitX,
                       noise_handler=self.noiseHandler,
                       noise_change_sigma_exponent=self.noiseChangeSigmaExponent,
                       bipop=self.bipop)

        opti_params = res[0]
        opti_val = res[1]
        iterations = res[4]

        return opti_params, opti_val, iterations

    def _set_options(self, kwargs):
        # get default options
        opt_dict = cma.CMAOptions()

        # set options
        opt_dict['bounds'] = [self.lowerBound, self.upperBound]
        opt_dict['tolx'] = self.optiAbsxTol
        opt_dict['tolfun'] = self.optiAbsfTol
        opt_dict['maxiter'] = self.maxNumOptiIterations

        if not self.verbose:
            # '-9' is 'very quite' according to documentation
            opt_dict['verbose'] = -9
        opt_dict['verb_log'] = False
        # add additional options
        for opt in kwargs.keys():
            opt_dict[opt] = kwargs[opt]

        return opt_dict