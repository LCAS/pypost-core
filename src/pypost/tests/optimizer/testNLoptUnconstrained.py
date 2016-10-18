from src.pypost.optimizer.nloptOptimizers.NLoptOptimizer import NLoptBoxConstrained
from scipy.optimize import rosen
from scipy.optimize import rosen_der
from scipy.optimize import rosen_hess
import pypost.common.SettingsManager as SettingsManager
import numpy as np
import nlopt

def rosenbrock(x):
    return (1 - x[0]) ** 2 + 100*(x[1] - x[0] ** 2) ** 2


optimizerName = 'myOptimizer'

settings = SettingsManager.getDefaultSettings()
#settings.setProperty(optimizerName + 'maxNumIterations', 500)
settings.setProperty(optimizerName + 'method', nlopt.LN_SBPLX)

lower_bound = np.asarray([5,5])
optimizer = NLoptBoxConstrained(2, optimizationName=optimizerName)
optimizer.verbose = True
optimizer.expParameterTransform = np.asarray([False, False])

params, value, iterations = optimizer.optimize(rosen, x0=np.asarray([6,6]), jacobian=rosen_der, lowerBound=lower_bound)
print(params, value, iterations)