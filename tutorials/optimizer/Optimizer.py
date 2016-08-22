import numpy as np
from pypost.common import SettingsManager
from pypost.optimizer.cma_es.CMA_ES import  CMA_ES
from pypost.optimizer.scipyOptimizers.SciPyBoxConstrained import SciPyBoxConstrained
from pypost.optimizer.scipyOptimizers.SciPyBoxConstrained import SciPyBoxConstrainedAlgorithms

#from pypost.optimizer.nloptOptimizers.NLoptOptimizer import NLoptBoxConstrained
from scipy.io import loadmat
from tutorials.optimizer.dualFunctionREPS import dualFunction
from time import perf_counter as pc
#import nlopt
from scipy.optimize import minimize

# load and prepare data
data = loadmat('data/reps_data.mat')
parameters = data['params']
reps_data = data['repsData']


def objective_function(x):
    return dualFunction(x, reps_data)

def func_only(x):
    g, gd=dualFunction(x, reps_data)
    return g

def grad_only(x):
    g, gd = dualFunction(x, reps_data)
    return gd
optimizerName = 'bla'

settings = SettingsManager.getDefaultSettings()
settings.setProperty(optimizerName + 'maxNumIterations', 10000)
settings.setProperty(optimizerName + 'OptiMaxEval',10000)
settings.setProperty(optimizerName + 'OptiAbsfTol', 1e-8)
settings.setProperty(optimizerName + 'OptiAbsxTol', 1e-8)
settings.setProperty(optimizerName + 'method', SciPyBoxConstrainedAlgorithms.TNC)


#settings.setProperty(optimizerName + 'method', nlopt.LD_TNEWTON)
#g, gd = dualFunction(parameters, reps_data)
#print(g, gd)

upperBound = 1e20 * np.ones(301)
upperBound[300] = 1e12
lowerBound = -1e20 * np.ones(301)
lowerBound[300] = 1e-12


optimizer = SciPyBoxConstrained(301, optimizationName=optimizerName)
#optimizer = NLoptBoxConstrained(301, optimizationName=optimizerName)
#optimizer = CMA_ES(301, optimizationName=optimizerName)

#print('res')
optimizer.verbose = True

x0 = np.zeros(301)
x0[300] = 1

parameters = np.squeeze(parameters)
t = pc()
params, value, iterations = optimizer.optimize(func=objective_function,
                                               x0=x0,
                                               lowerBound=lowerBound,
                                               upperBound=upperBound,
                                               gradient=True
                                               )
elapsed_time = pc() - t
print('best val =',  value, 'needed', elapsed_time, 'sec')




#print('bla')