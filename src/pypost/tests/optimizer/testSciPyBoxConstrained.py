from src.pypost.optimizer.scipyOptimizers.SciPyBoxConstrained import SciPyBoxConstrained
from scipy.optimize import rosen
from scipy.optimize import rosen_der
import pypost.common.SettingsManager as SettingsManager
import numpy as np

def rosenbrock(x):
    return (1 - x[0]) ** 2 + 100*(x[1] - x[0] ** 2) ** 2


optimizerName = 'myOptimizer'

settings = SettingsManager.getDefaultSettings()
settings.setProperty(optimizerName + 'maxNumIterations', 500)
settings.setProperty(optimizerName + 'method', 'BFGS')

lower_bound = np.asarray([5,5])

optimizer = SciPyBoxConstrained(2, lowerBound=lower_bound, optimizationName=optimizerName)
optimizer.verbose = True
optimizer.expParameterTransform = np.asarray([False, False])

params, value, iterations = optimizer.optimize(rosen)
print(params, value, iterations)

