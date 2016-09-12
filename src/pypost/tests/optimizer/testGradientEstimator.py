from scipy.optimize import rosen, rosen_der
from pypost.optimizer.GradientEstimation import GradientEstimator
import unittest
import numpy as np


class testGradientEstimator(unittest.TestCase):
    def setUp(self):
        self.epsilon = 1e-6
        self.estimator = GradientEstimator(rosen, 2, self.epsilon)

    def testEstimation(self):
        values = np.random.uniform(-5.0, 5.0, size=[10, 2])
        for i in range(10):
            true_grad = rosen_der(values[i, :])
            pred_grad = self.estimator.simpleFiniteDifferences(values[i, :])
            self.assertAlmostEqual(true_grad[0], pred_grad[0], 4)
        self.assertAlmostEqual(true_grad[1], pred_grad[1], 4)