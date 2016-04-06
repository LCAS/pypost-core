import numpy as np
import os
import sys
import unittest
sys.path.append(
    os.path.abspath(os.path.dirname(os.path.realpath(__file__))+'/../../src'))
from parametricModels.ParametricModel import ParametricModel


class testParametricModel(unittest.TestCase):

    def test_registerGradientModelFunction(self):
        class ParametricModelWithTestVariables(ParametricModel):
            def __init__(self):
                self.inputVariables = ['context', 'parameters']
                self.outputVariables = ['return']
                self.numParameters = 10

            def getLikelihoodGradient(self):
                return np.zeros(self.numParameters, 1)

        p = ParametricModelWithTestVariables()
        self.assertRaises(NotImplementedError, p.registerGradientModelFunction)

    def test_getFisherInformationMatrix_abstract(self):
        p = ParametricModel()
        self.assertRaises(NotImplementedError, p.getFisherInformationMatrix)

    def test_getLikelihoodGradient_abstract(self):
        p = ParametricModel()
        self.assertRaises(NotImplementedError, p.getLikelihoodGradient)

if __name__ == '__main__':
    unittest.main()
