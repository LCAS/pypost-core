import numpy as np
import math
from abc import abstractmethod


class HyperParameterObject(object):

    def getMinHyperParameterRange(self):
        params = self.getHyperParameters()
        expParameterTransformMap = self.getExpParameterTransformMap()
        params[expParameterTransformMap] =\
            params[expParameterTransformMap].dot(math.pow(10, -10))
        # TODO: check this ('not')
        params[not expParameterTransformMap] = \
            params[not expParameterTransformMap].dot(0.1)
        return params

    def getMaxHyperParameterRange(self):
        params = self.getHyperParameters()
        expParameterTransformMap = self.getExpParameterTransformMap()
        params[expParameterTransformMap] =\
            params[expParameterTransformMap].dot(math.pow(10, 10))
        params[not expParameterTransformMap] =\
            params[not expParameterTransformMap] * 10
        return params

    def getExpParameterTransformMap(self):
        return np.ones((1, self.getNumHyperParameters()))

    @abstractmethod
    def getNumHyperParameters(self):
        pass

    @abstractmethod
    def setHyperParameters(self, params):
        pass

    @abstractmethod
    def getHyperParameters(self):
        pass
