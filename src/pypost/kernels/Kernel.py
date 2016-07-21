# -*- coding: utf-8 -*-
# Skipped methods from original implementation:
# createKernelSQEPeriodic

import numpy as np
from abc import abstractmethod
from pypost.learner.parameterOptimization.HyperParameterObject import \
    HyperParameterObject


class Kernel(HyperParameterObject):

    def __init__(self, num_dims, kernel_name=None):
        # Dimensionality of the data the kernel is working with
        self.numDims = num_dims
        self.kernelName = kernel_name

        self._kernelTag = 1

    # Evaluates kernel for all elements
    # Compute gram matrix of the form
    #  -----------------------------
    #  | k(x₁,y₁) | k(x₁,y₂) | ... |
    #  -----------------------------
    #  | k(x₂,y₁) | k(x₂,y₂) | ... |
    #  -----------------------------
    #  | ...      | ...      | ... |
    #  -----------------------------
    @abstractmethod
    def getGramMatrix(self, X, Y):
        pass

    # Returns the diagonal of the gram matrix
    # which means the kernel is evaluated between every data point and itself
    def getGramDiag(self, data):
        diag = np.zeros(data.shape[0])

        for i in range(data.shape[0]):
            diag[i] = self.getGramMatrix(data[i, :], data[i, :])

    @abstractmethod
    def getKernelDerivParam(self, data):
        pass

    @abstractmethod
    def getKernelDerivData(self, ref_data, cur_data):
        pass

    @abstractmethod
    def getNumHyperParameters(self):
        pass

    @abstractmethod
    def getHyperParameters(self):
        pass

    @abstractmethod
    def setHyperParameters(self, params):
        self._kernelTag += 1

    # NEVER USED
    def getKernelTag(self):
        return self._kernelTag
