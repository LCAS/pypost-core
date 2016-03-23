import numpy as np
import os
import sys
import unittest
sys.path.append(
    os.path.abspath(os.path.dirname(os.path.realpath(__file__))+'/../../src'))
from data.DataManager import DataManager
from parametricModels.ParametricFunction import ParametricFunction

class testParametricFunction(unittest.TestCase):

    def test_registerGradientFunction(self):
        class ParametricFunctionWithTestVariables1(ParametricFunction):
            def __init__(self):
                self.inputVariables = np.ndarray((1, 2))
                self.numParameters = 10
                self.dataManager = DataManager('testDataManager')

        p = ParametricFunctionWithTestVariables1()
        p.registerGradientFunction()

        class ParametricFunctionWithTestVariables2(ParametricFunction):
            def __init__(self):
                self.inputVariables = None
                self.outputVariable = 'return'

        q = ParametricFunctionWithTestVariables2()
        self.assertRaises(NotImplementedError, q.registerGradientFunction)




    def test_registerGradientDataEntry(self):
        class ParametricFunctionWithTestVariables(ParametricFunction):
            def __init__(self):
                self.outputVariable = 'return'
                self.numParameters = 10
                self.dataManager = DataManager('testDataManager')

        p = ParametricFunctionWithTestVariables()
        p.registerGradientDataEntry()
        self.assertTrue('returnGrad' in p.dataManager.dataEntries)

    def test_getGradient_abstract(self):
        p = ParametricFunction()
        self.assertRaises(NotImplementedError, p.getGradient)

    def test_getNumParameters_abstract(self):
        p = ParametricFunction()
        self.assertRaises(NotImplementedError, p.getNumParameters)

    def test_setParameterVector_abstract(self):
        p = ParametricFunction()
        self.assertRaises(NotImplementedError, p.setParameterVector, 0.1)

if __name__ == '__main__':
    unittest.main()
