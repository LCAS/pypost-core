from src.pypost.optimizer.scipyOptimizers.SciPyUnconstrained import SciPyUnconstrained
from src.pypost.optimizer.scipyOptimizers.SciPyUnconstrained import SciPyUnconstrainedAlgorithms
from scipy.optimize import rosen
from scipy.optimize import rosen_der
from scipy.optimize import rosen_hess
import pypost.common.SettingsManager as SettingsManager
import numpy as np

def rosenbrock(x):
    return (1 - x[0]) ** 2 + 100*(x[1] - x[0] ** 2) ** 2


optimizerName = 'myOptimizer'

settings = SettingsManager.getDefaultSettings()
settings.setProperty(optimizerName + 'maxNumIterations', 500)
settings.setProperty(optimizerName + 'method', SciPyUnconstrainedAlgorithms.BFGS)

optimizer = SciPyUnconstrained(2, optimizationName=optimizerName)
#optimizer.verbose = True
optimizer.expParameterTransform = np.asarray([False, False])

params, value, iterations = optimizer.optimize(rosen, rosen_der, rosen_hess)
print(params, value, iterations)





