import time
import numpy as np
from scipy.io import loadmat
from pypost.common import SettingsManager
from pypost.optimizer import SciPyBoxConstrained
from pypost.optimizer import SciPyBoxConstrainedAlgorithms
from tutorials.optimizer.dualFunctionREPS import dualFunction

# WARNING!! Executing this may take a while since SLSQP
# In this tutorial we are going to see how to use the PyPoST optimizer.
# Based on an example data set we optimize the cost function of REPS (Relative Entropy Policy Search)

# First we need to load and prepare the example data
data = loadmat('data/reps_data.mat')
parameters = data['params']
reps_data = data['repsData']

# We are optimizing the dual function which has 301 parameters
num_of_parameters = 301

# Next we define our objective function, to show the different modes of the optimizer we specify
# 1.) The 'whole' objective function, returning both, the function value and the gradient at a specific value x
def objective_function(x):
    return dualFunction(x, reps_data)

# 2.) A function returning only the value (note that this implementation is inefficient since the gradient is computed
#     nevertheless and then discarded)
def func_only(x):
    g, _ = dualFunction(x, reps_data)
    return g

# 3.) And a function returning only the gradient (note that this implementation is inefficient since the value is
#     computed nevertheless and then discarded)
def grad_only(x):
    g, gd = dualFunction(x, reps_data)
    return gd

# Next we specify the bounds of our algorithm
upperBound = 1e20 * np.ones(301)
upperBound[300] = 1e12
lowerBound = -1e20 * np.ones(301)
# this is particular important since it prevents the lagrangian multiplier from becoming non-positive
lowerBound[300] = 1e-12

# We give a name to our optimizer, get the default settings ...
optimizerName = 'testOptimizer'
settings = SettingsManager.getDefaultSettings()

# And set some termination conditions.
settings.setProperty(optimizerName + 'maxNumIterations', 10000)
settings.setProperty(optimizerName + 'OptiMaxEval', 10000)
settings.setProperty(optimizerName + 'OptiAbsfTol', 1e-8)
settings.setProperty(optimizerName + 'OptiAbsxTol', 1e-8)

# Next we specify the optimizer we want to use, since we have a box constrained problem we need to use a algorithm
# capable of dealing with this, we chose L-BFGS-B
settings.setProperty(optimizerName + 'method', SciPyBoxConstrainedAlgorithms.L_BFGS_B)

# initializing the optimizer ...
optimizer = SciPyBoxConstrained(301, optimizationName=optimizerName)
# ... setting verbose to True so we can see whats going on
optimizer.verbose = True

# preparing the initial value
parameters = np.squeeze(parameters)
t_start = time.time()
# start the optimization, we use the 'whole' objective function and set 'gradient=True' in order to tell the optimizer
# that the gradient is returned by the objective function
params, value, iterations = optimizer.optimize(func=objective_function,
                                               x0=parameters,
                                               lowerBound=lowerBound,
                                               upperBound=upperBound,
                                               gradient=True
                                               )
print('best val =',  value, 'needed', time.time() - t_start, 'sec')

# For the second run we use separate functions for the objective and its gradient ...
t_start = time.time()
params, value, iterations = optimizer.optimize(func=func_only,
                                               x0=parameters,
                                               lowerBound=lowerBound,
                                               upperBound=upperBound,
                                               gradient=grad_only
                                               )
print('best val =',  value, 'needed', time.time() - t_start, 'sec')
