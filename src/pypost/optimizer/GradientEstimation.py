import numpy as np
from scipy.optimize import approx_fprime

class GradientEstimator:

    def __init__(self, function, numParams, epsilon = 1e-6):
        self.function = function
        self.numParams = numParams
        self.epsilon = epsilon


    def simpleFiniteDifferences(self, x):
        gradient = np.zeros(self.numParams)
        x_temp = np.copy(x)
        for i in range(self.numParams):
            x_temp[i] = x[i] + self.epsilon
            val_1 = self.function(x_temp)

            x_temp[i] = x[i] - self.epsilon
            val_2 = self.function(x_temp)

            gradient[i] = (val_1 - val_2) / (2 * self.epsilon)
            x_temp[i] = x[i]
        return gradient

    def scipyFiniteDifferences(self, x):
        return approx_fprime(x, self.function, self.epsilon)
