from pypost.optimizer.SciPyBasedUnconstrained import SciPyBasedUnconstrained
from scipy.optimize import rosen
from scipy.optimize import rosen_der
import pypost.common.SettingsManager as SettingsManager
import numpy as np

def rosenbrock(x):
    return (1 - x[0]) ** 2 + 100*(x[1] - x[0] ** 2) ** 2


optimizerName = 'myOptimizer'

settings = SettingsManager.getDefaultSettings()
settings.setProperty(optimizerName + 'maxNumIterations', 500)
settings.setProperty(optimizerName + 'method', 'CG')

optimizer = SciPyBasedUnconstrained(2, optimizationName=optimizerName)
optimizer.verbose = False
optimizer.expParameterTransform = np.asarray([False, False])

params, value, iterations = optimizer.optimize(rosen)
print(params, value, iterations)





