import numpy as np
import math
from abc import abstractmethod


class HyperParameterObject(object):

    def getMinHyperParameterRange(self):
        params = self.getHyperParameters()
        expParameterTransformMap = self.getExpParameterTransformMap()
        params[expParameterTransformMap] =\
            params[expParameterTransformMap].dot(1e-10)
        # TODO: check this ('not')
        params[not expParameterTransformMap] = \
            params[not expParameterTransformMap].dot(0.1)
        return params

    def getMaxHyperParameterRange(self):
        params = self.getHyperParameters()
        expParameterTransformMap = self.getExpParameterTransformMap()
        params[expParameterTransformMap] =\
            params[expParameterTransformMap].dot(1e10)
        params[not expParameterTransformMap] =\
            params[not expParameterTransformMap] * 10
        return params

    def getExpParameterTransformMap(self):
        return np.ones(self.getNumHyperParameters(), dtype=np.bool)

    @abstractmethod
    def getNumHyperParameters(self):
        pass

    @abstractmethod
    def setHyperParameters(self, params):
        pass

    @abstractmethod
    def getHyperParameters(self):
        pass
