import unittest
import sys
import numpy as np
sys.path.append('../src/data')
import DataUtil
from DataManipulator import DataManipulator

class TestManipulator(DataManipulator):
    
    def __init__(self, dataManager):
        super().__init__(dataManager)
        self.addDataManipulationFunction(self.sampleParameters, [], ['parameters'])
    
    def sampleParameters(self, numElements):
        return np.ones((numElements, 10))


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
        
    def test_callDataManipulationFunction(self):
        dataManager = DataUtil.createTestManager()
        data = dataManager.getDataObject([20, 30, 40])

        manipulator = TestManipulator(dataManager)
        
        self.assertTrue('sampleParameters' in manipulator._manipulationFunctions)
        
        data.setDataEntry(['parameters'], [...], 7 * np.ones((20, 10)))
        self.assertTrue((data.getDataEntry(['parameters'], [...]) ==
                          7 * np.ones((20, 10))).all())
        
        manipulator.callDataFunction('sampleParameters', data, [...])
        self.assertTrue((data.getDataEntry(['parameters'], [...]) ==
                          np.ones((20, 10))).all())
        
        data.setDataEntry(['parameters'], [...], 7 * np.ones((20, 10)))
        self.assertTrue((data.getDataEntry(['parameters'], [...]) ==
                          7 * np.ones((20, 10))).all())
        
        manipulator.callDataFunction('sampleParameters', data, [slice(0,10)])
        self.assertTrue((data.getDataEntry(['parameters'], [...]) == 
                         np.vstack((np.ones((10, 10)), 7 * np.ones((10,10))))).all())

if __name__ == '__main__':
    unittest.main()
