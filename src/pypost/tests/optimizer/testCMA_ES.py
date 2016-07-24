from pypost.optimizer.cma_es.CMA_ES import CMA_ES
from scipy.optimize import rosen
from scipy.optimize import rosen_der
from scipy.optimize import rosen_hess
import pypost.common.SettingsManager as SettingsManager
import numpy as np

def rosenbrock(x):
    return (1 - x[0]) ** 2 + 100*(x[1] - x[0] ** 2) ** 2


optimizerName = 'myOptimizer'

settings = SettingsManager.getDefaultSettings()
#settings.setProperty(optimizerName + 'maxNumIterations', 500)
#settings.setProperty(optimizerName + 'method', 'CG')
lower_bound = np.asarray([5,5])
optimizer = CMA_ES(2, optimizationName=optimizerName)
optimizer.verbose = True
optimizer.isMaximize = True

params, value, iterations = optimizer.optimize(rosen, x0=np.asarray([6,6]), gradient=rosen_der, lowerBound=lower_bound)
print(params, value, iterations)