import unittest
from src.pypost.optimizer import SciPyUnconstrained, SciPyUnconstrainedAlgorithms
from scipy.optimize import rosen, rosen_der
import pypost.common.SettingsManager as SettingsManager
import numpy as np


def rosen_func_and_der(x):
    return rosen(x), rosen_der(x)


def rosen_inv(x):
    return - rosen(x)


def rosen_der_inv(x):
    return - rosen_der(x)


class testSciPyUnconstrained(unittest.TestCase):
    def setUp(self):
        self.optimizerName = 'rosen_optimizer'
        self.settings = SettingsManager.getDefaultSettings()
        self.settings.setProperty(self.optimizerName + 'method', SciPyUnconstrainedAlgorithms.CG)

        self.optimizer = SciPyUnconstrained(2, optimizationName=self.optimizerName)
        # use this, else we start directly at the optimum
        self.x0 = np.asarray([5, 5])
        self.reference_params, self.reference_value, _ = self.optimizer.optimize(rosen, rosen_der, self.x0)

    def testOptimizer(self):
        self.settings.setProperty(self.optimizerName + 'maxNumIterations', 10)
        params, value, iterations = self.optimizer.optimize(rosen, gradient=rosen_der, x0=self.x0)
        self.assertLessEqual(iterations, 10)
        self.settings.setProperty(self.optimizerName + 'maxNumIterations', 100)

    def testMaximization(self):
        self.optimizer.isMaximize = True
        rosen_inv = lambda x: - rosen(x)
        rosen_der_inv = lambda x: - rosen_der(x)
        max_params, max_value, _ = self.optimizer.optimize(rosen_inv, rosen_der_inv, x0=self.x0)
        self.assertAlmostEqual(self.reference_value, max_value, 10)
        self.assertAlmostEqual(self.reference_params[0], max_params[0], 4)
        self.assertAlmostEqual(self.reference_params[1], max_params[1], 4)

    def testGradientPassing(self):
        joint_params, joint_value, _ = self.optimizer.optimize(rosen_func_and_der, True, x0=self.x0)
        self.assertAlmostEqual(self.reference_value, joint_value, 10)
        self.assertAlmostEqual(self.reference_params[0], joint_params[0], 4)
        self.assertAlmostEqual(self.reference_params[1], joint_params[1], 4)

   # def testLogSpaceOptimization(self):
   #     self.optimizer.expParameterTransform = np.asarray([True, True])
   #     rosen_exp = lambda x: np.exp(rosen(x + 1))
   #     rosen_der_exp = lambda x: np.exp(rosen_der(x + 1))
   #     x0 = np.asarray([2, 2])
   #     trans_params, trans_value, _ = self.optimizer.optimize(rosen_exp, rosen_der_exp, x0=x0)
   #     self.assertAlmostEqual(self.reference_value, trans_value, 10)
   #     self.assertAlmostEqual(self.reference_params[0], trans_params[0], 4)
   #     self.assertAlmostEqual(self.reference_params[1], trans_params[1], 4)





