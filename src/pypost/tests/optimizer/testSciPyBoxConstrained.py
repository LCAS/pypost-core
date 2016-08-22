from src.pypost.optimizer.scipyOptimizers.SciPyBoxConstrained import SciPyBoxConstrained
from src.pypost.optimizer.scipyOptimizers.SciPyBoxConstrained import SciPyBoxConstrainedAlgorithms
from scipy.optimize import rosen
from scipy.optimize import rosen_der
import pypost.common.SettingsManager as SettingsManager
import numpy as np
def rosenbrock(x):
    return (1 - x[0]) ** 2 + 100*(x[1] - x[0] ** 2) ** 2

def inv_rosen(x):
    return -rosen(x)
optimizerName = 'myOptimizer'

settings = SettingsManager.getDefaultSettings()
settings.setProperty(optimizerName + 'maxNumIterations', 100)
settings.setProperty(optimizerName + 'method', SciPyBoxConstrainedAlgorithms.TNC)

lower_bound = np.asarray([5,5])

optimizer = SciPyBoxConstrained(2, optimizationName=optimizerName)
optimizer.verbose = True
optimizer.isMaximize = True

optimizer.expParameterTransform = np.asarray([False, False])

params, value, iterations = optimizer.optimize(inv_rosen, x0=np.asarray([5,5]),lowerBound=lower_bound)
print(params, value, iterations)

