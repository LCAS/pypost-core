import unittest
import sys
import numpy as np
sys.path.append('../src/data')
import DataUtil
from DataManipulator import DataManipulator


class testDataManipulator(unittest.TestCase):
    
    def test_addDataManipulationFunction(self):
        dataManager = DataUtil.createTestManager()
        manipulator = DataManipulator(dataManager)
        
        def f(numElements):
            return np.ones((numElements, 10))
        
        manipulator.addDataManipulationFunction(f, [], ['parameters'])

        manipulationFunction = manipulator._manipulationFunctions['f']
        self.assertIsNotNone(manipulationFunction)
        self.assertEqual(manipulationFunction.function, f)
        self.assertEqual(manipulationFunction.inputArguments, [])
        self.assertEqual(manipulationFunction.outputArguments, ['parameters'])
        
        samplerFunction = manipulator._samplerFunctions['f']
        self.assertIsNotNone(samplerFunction)
        self.assertEqual(manipulator._samplerFunctions['f'], ['f'])

if __name__ == '__main__':
    unittest.main()
