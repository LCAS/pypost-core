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
        self.addDataManipulationFunction(self.sampleParameters, [],
                                         ['parameters'])
        self.addDataManipulationFunction(self.sampleStates, ['parameters'],
                                         'states', CallType.PER_EPISODE, True)

    def sampleParameters(self, numElements):
        return np.ones((numElements, 5))

    def sampleStates(self, numElements, parameters):
        return np.ones((numElements, 1))


class testDataManipulator(unittest.TestCase):
    def test_init(self):
        self.assertRaises(ValueError, DataManipulator, None)

    def test_addDataManipulationFunction(self):
        dataManager = DataUtil.createTestManager()
        manipulator = DataManipulator(dataManager)

        def f(numElements):
            return np.ones((numElements, 10))
        
        def g(numElements, parameters):
            pass
        
        def h():
            pass

        manipulator.addDataManipulationFunction(f, [], ['parameters'])

        manipulationFunction = manipulator._manipulationFunctions['f']
        self.assertEqual(str(manipulationFunction), "f: [] -> ['parameters']")
        self.assertIsNotNone(manipulationFunction)
        self.assertEqual(manipulationFunction.function, f)
        self.assertEqual(manipulationFunction.inputArguments, [])
        self.assertEqual(manipulationFunction.outputArguments, ['parameters'])
        
        # Add alias to f
        manipulator.addDataFunctionAlias('g', 'f', False)

        # Now add new function of same name, the alias should then be overwritten
        manipulator.addDataManipulationFunction(g, 'parameters', [])
        self.assertEqual(manipulator._samplerFunctions['g'], ['g'])
        self.assertEqual(manipulationFunction.depthEntry, 'parameters')

        samplerFunction = manipulator._samplerFunctions['f']
        self.assertIsNotNone(samplerFunction)
        self.assertEqual(manipulator._samplerFunctions['f'], ['f'])
        
        # Add function without input or output. The depth entry should be ''
        manipulator.addDataManipulationFunction(h, [], [])
        self.assertEqual(manipulator._manipulationFunctions['h'].depthEntry, '')

    def test_isSamplerFunction(self):
        dataManager = DataUtil.createTestManager()
        manipulator = DataManipulator(dataManager)

        def f(numElements):
            return np.ones((numElements, 10))

        manipulator.addDataManipulationFunction(f, [1], ['parameters'])
        self.assertTrue(manipulator.isSamplerFunction('f'))
        self.assertFalse(manipulator.isSamplerFunction('g'))

    def test_addDataFunctionAlias(self):
        dataManager = DataUtil.createTestManager()
        data = dataManager.getDataObject([20, 30, 40])

        manipulator = TestManipulator(dataManager)

        self.assertRaises(ValueError, manipulator.addDataFunctionAlias,
                          'alias', 'sampleChocolate')

        self.assertTrue('sampleParameters' in
                        manipulator._manipulationFunctions)
        self.assertTrue('sampleStates' in manipulator._manipulationFunctions)

        manipulator.addDataFunctionAlias('alias', 'sampleParameters')
        self.assertEqual(manipulator._samplerFunctions['alias'],
                         ['sampleParameters'])

        manipulator.addDataFunctionAlias('alias', 'sampleStates')
        self.assertEqual(manipulator._samplerFunctions['alias'],
                         ['sampleParameters', 'sampleStates'])

        manipulator.clearDataFunctionAlias('alias')
        self.assertTrue('alias' not in manipulator._samplerFunctions)

        manipulator.addDataFunctionAlias('alias', 'sampleStates')
        self.assertEqual(manipulator._samplerFunctions['alias'],
                         ['sampleStates'])

        manipulator.addDataFunctionAlias('alias', 'sampleParameters', True)
        self.assertEqual(manipulator._samplerFunctions['alias'],
                         ['sampleParameters', 'sampleStates'])
        
    def test_setIndices(self):
        dataManager = DataUtil.createTestManager()
        data = dataManager.getDataObject([20, 30, 40])

        manipulator = TestManipulator(dataManager)
        
        self.assertRaises(ValueError, manipulator.setIndices, 'nonExistant', 0, 0)
        self.assertEqual(manipulator._manipulationFunctions['sampleStates'].indices, [None])
        manipulator.setIndices('sampleStates', 0, ...)
        self.assertEqual(manipulator._manipulationFunctions['sampleStates'].indices, [...])
        self.assertRaises(ValueError, manipulator.setIndices, 'sampleStates', 1, ...)
        
    def test_setData(self):
        dataManager = DataUtil.createTestManager()
        data = dataManager.getDataObject([20, 30, 40])

        manipulator = TestManipulator(dataManager)
        
        self.assertRaises(ValueError, manipulator.setTakesData, 'nonExistant', True)
        self.assertFalse(manipulator._manipulationFunctions['sampleStates'].takesData)
        manipulator.setTakesData('sampleStates', True)
        self.assertTrue(manipulator._manipulationFunctions['sampleStates'].takesData)

    def test_callDataFunction(self):
        dataManager = DataUtil.createTestManager()
        data = dataManager.getDataObject([20, 30, 40])

        manipulator = TestManipulator(dataManager)

        self.assertTrue('sampleParameters' in
                        manipulator._manipulationFunctions)
        self.assertTrue('sampleStates' in manipulator._manipulationFunctions)

        self.assertRaises(ValueError, manipulator.callDataFunction, 'nonExistant', data, [...])

        data.setDataEntry('parameters', [...], 7 * np.ones((20, 5)))
        self.assertTrue((data.getDataEntry('parameters', [...]) ==
                         7 * np.ones((20, 5))).all())

        manipulator.callDataFunction('sampleParameters', data, [...])
        self.assertTrue((data.getDataEntry('parameters', [...]) ==
                         np.ones((20, 5))).all())

        data.setDataEntry('parameters', [...], 7 * np.ones((20, 5)))
        self.assertTrue((data.getDataEntry('parameters', [...]) ==
                         7 * np.ones((20, 5))).all())

        data.setDataEntry(['parameters'], [slice(0, 10)], np.ones((10, 5)))

        manipulator.callDataFunction('sampleParameters', data, [slice(0, 5)])
        self.assertTrue((data.getDataEntry('parameters', [...]) ==
                         np.vstack((np.ones((10, 5)),
                                    7 * np.ones((10, 5))))).all())

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
                         7 * np.ones((570, 1))).all())
        
        def singleSampleFunction(numElements):
            return 12 * np.ones((numElements, 1))
        
        manipulator.addDataManipulationFunction(singleSampleFunction, [], ['states'], CallType.SINGLE_SAMPLE, True)
        
        manipulator.callDataFunction('singleSampleFunction', data, [..., ...])
        print(data.getDataEntry('states', [..., ...]))
        result = data.getDataEntry('states', [..., ...])
        self.assertTrue(result.shape == (600, 1))
        self.assertTrue((result == 12 * np.ones((600, 1))).all())
        
    def test_callDataFunctionOutput(self):
        dataManager = DataUtil.createTestManager()
        data = dataManager.getDataObject([20, 30, 40])

        manipulator = TestManipulator(dataManager)

        self.assertTrue('sampleParameters' in
                        manipulator._manipulationFunctions)
        self.assertTrue('sampleStates' in manipulator._manipulationFunctions)
        
        self.assertRaises(ValueError, manipulator.callDataFunctionOutput, 'notExistant', data, [...])

        parameters = manipulator.callDataFunctionOutput('sampleParameters', data, [...])
        self.assertTrue((parameters == np.ones((20, 5))).all())

        parameters = manipulator.callDataFunctionOutput('sampleParameters', data, [slice(0, 10)])
        self.assertTrue((parameters == np.ones((10, 5))).all())

        states = manipulator.callDataFunctionOutput('sampleStates', data, [..., ...])
        self.assertTrue((states == np.ones((600, 1))).all())

        states = manipulator.callDataFunctionOutput('sampleStates', data, [slice(0, 1), ...])
        self.assertTrue((states == np.ones((30, 1))).all())
        
        manipulator.setIndices('sampleStates', 0, slice(0,1))
        states = manipulator.callDataFunctionOutput('sampleStates', data, [..., ...])
        self.assertTrue((states == np.ones((600, 1))).all())
        
        def functionWithoutNumElements(parameters):
            return 7 * np.ones(parameters.shape)
        
        manipulator.addDataManipulationFunction(functionWithoutNumElements, ['parameters'],
                                         'parameters', CallType.ALL_AT_ONCE, False)
        
        parameters = manipulator.callDataFunctionOutput('functionWithoutNumElements', data, [slice(0,10)])
        self.assertTrue((parameters == 7 * np.ones((10, 5))).all())
        
        def functionTakesData(numElements, data):
            return 9 * np.ones((numElements, 5))
        
        manipulator.addDataManipulationFunction(functionTakesData, [], ['parameters'], CallType.ALL_AT_ONCE, True)
        manipulator.setTakesData('functionTakesData', True)
        
        parameters = manipulator.callDataFunctionOutput('functionTakesData', data, [...])
        self.assertTrue((parameters == 9 * np.ones((20, 5))).all())
if __name__ == '__main__':
    unittest.main()
