import unittest
from pypost.optimizer.SciPyBoxConstrained import SciPyBoxConstrained, SciPyBoxConstrainedAlgorithms
from scipy.optimize import rosen, rosen_der
import pypost.common.SettingsManager as SettingsManager
import numpy as np


# Also responsible for testing (abstract) 'boxConstrained' class

class testSciPyBoxConstrained(unittest.TestCase):
    def setUp(self):
        self.optimizerName = 'myOptimizer'
        self.settings = SettingsManager.getDefaultSettings()
        self.settings.setProperty(self.optimizerName + 'maxNumIterations', 100)
        self.settings.setProperty(self.optimizerName + 'method', SciPyBoxConstrainedAlgorithms.L_BFGS_B)
        self.optimizer = SciPyBoxConstrained(2, optimizationName=self.optimizerName)

    def testLowerBound(self):
        lower_bound = np.asarray([5, 5])
        params, value, iterations = self.optimizer.optimize(rosen, rosen_der,
                                                            x0=np.asarray([8, 8]), lowerBound=lower_bound)
        self.assertTrue((params >= lower_bound).all())

    def testUpperBound(self):
        upper_bound = np.asarray([-5, -5])
        params, value, iterations = self.optimizer.optimize(rosen, rosen_der,
                                                            x0=np.asarray([-8, -8]), upperBound=upper_bound)

        self.assertTrue((params <= upper_bound).all())