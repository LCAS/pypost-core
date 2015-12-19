import unittest
import sys
import numpy as np
sys.path.append('../src/data')
sys.path.append('../src/interfaces')
import DataUtil
from DataManipulator import DataManipulator
from DataManipulator import CallType

class TestManipulator(DataManipulator):
    
    def __init__(self, dataManager):
        super().__init__(dataManager)
        self.addDataManipulationFunction(self.sampleParameters, [], ['parameters'])
        self.addDataManipulationFunction(self.sampleStates, ['parameters'],
                                          'states', CallType.PER_EPISODE, True)
    
    def sampleParameters(self, numElements):
        return np.ones((numElements, 10))
    
    def sampleStates(self, numElements, parameters):
        return np.ones((numElements, 1))

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
    
    def test_addDataFunctionAlias(self):
        dataManager = DataUtil.createTestManager()
        data = dataManager.getDataObject([20, 30, 40])
        
        manipulator = TestManipulator(dataManager)

        self.assertRaises(ValueError, manipulator.addDataFunctionAlias, 'alias', 'sampleChocolate')
        
        self.assertTrue('sampleParameters' in manipulator._manipulationFunctions)
        self.assertTrue('sampleStates' in manipulator._manipulationFunctions)
        
        manipulator.addDataFunctionAlias('alias', 'sampleParameters')
        self.assertEqual(manipulator._samplerFunctions['alias'], ['sampleParameters'])
        
        manipulator.addDataFunctionAlias('alias', 'sampleStates')
        self.assertEqual(manipulator._samplerFunctions['alias'], ['sampleParameters', 'sampleStates'])
        
        manipulator.clearDataFunctionAlias('alias')
        self.assertTrue('alias' not in manipulator._samplerFunctions)
        
        manipulator.addDataFunctionAlias('alias', 'sampleStates')
        self.assertEqual(manipulator._samplerFunctions['alias'], ['sampleStates'])
        
        manipulator.addDataFunctionAlias('alias', 'sampleParameters', True)
        self.assertEqual(manipulator._samplerFunctions['alias'], ['sampleParameters', 'sampleStates'])
        
    def test_callDataManipulationFunction(self):
        dataManager = DataUtil.createTestManager()
        data = dataManager.getDataObject([20, 30, 40])

        manipulator = TestManipulator(dataManager)
        
        self.assertTrue('sampleParameters' in manipulator._manipulationFunctions)
        self.assertTrue('sampleStates' in manipulator._manipulationFunctions)
        
        data.setDataEntry('parameters', [...], 7 * np.ones((20, 10)))
        self.assertTrue((data.getDataEntry('parameters', [...]) ==
                          7 * np.ones((20, 10))).all())
        
        manipulator.callDataFunction('sampleParameters', data, [...])
        self.assertTrue((data.getDataEntry('parameters', [...]) ==
                          np.ones((20, 10))).all())
        
        data.setDataEntry('parameters', [...], 7 * np.ones((20, 10)))
        self.assertTrue((data.getDataEntry('parameters', [...]) ==
                          7 * np.ones((20, 10))).all())
        
        data.setDataEntry(['parameters'], [slice(0,10)], np.ones((10,10)))
                
        manipulator.callDataFunction('sampleParameters', data, [slice(0,10)])
        self.assertTrue((data.getDataEntry('parameters', [...]) == 
                         np.vstack((np.ones((10, 10)), 7 * np.ones((10,10))))).all())
        
        data.setDataEntry('states', [..., ...], 7 * np.ones((600, 1)))
        self.assertTrue((data.getDataEntry('states', [..., ...]) ==
                          7 * np.ones((600, 1))).all())
        
        manipulator.callDataFunction('sampleStates', data, [..., ...])
        self.assertTrue((data.getDataEntry('states', [..., ...]) ==
                         np.ones((600, 1))).all())
        
        data.setDataEntry('states', [..., ...], 7 * np.ones((600, 1)))
        self.assertTrue((data.getDataEntry('states', [..., ...]) ==
                          7 * np.ones((600, 1))).all())
        
        manipulator.callDataFunction('sampleStates', data, [slice(0, 1), ...])
        self.assertTrue((data.getDataEntry('states', [slice(0, 1), ...]) ==
                          np.ones((30, 1))).all())
        self.assertTrue((data.getDataEntry('states', [slice(1, 20), ...]) ==
                         7 * np.ones((570, 1)).all()))

if __name__ == '__main__':
    unittest.main()
