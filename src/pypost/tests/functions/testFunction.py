import unittest
import numpy as np
import math

from pypost.functions.Function import Function
from pypost.functions.MappingInterface import MappingInterface


class testFunction(unittest.TestCase):

    def test_init(self):
        f = Function()

        self.assertTrue(f.registerDataFunctions)
        self.assertTrue(isinstance(f, MappingInterface))

    def test_registerMappingInterfaceFunction(self):
        f = Function()

        f.registerDataFunctions = True
        f.addMappingFunctionCalled = False

        def addMappingFunction(function):
            f.addMappingFunctionCalled = True
        f.addMappingFunction = addMappingFunction

        f.registerMappingInterfaceFunction()

        self.assertTrue(f.addMappingFunctionCalled)

        g = Function()
        g.registerDataFunctions = False
        g.addMappingFunctionCalled = False

        def addMappingFunction(function):
            g.addMappingFunctionCalled = True
        g.addMappingFunction = addMappingFunction

        g.registerMappingInterfaceFunction()

        self.assertFalse(g.addMappingFunctionCalled)

    def test_getExpectation(self):
        f = Function()
        self.assertRaises(NotImplementedError, f.getExpectation, 0)
