import unittest
import numpy as np
from pypost.data.DataManipulator import DataManipulator
from pypost.data.DataManipulator import DataManipulationFunction
from pypost.data.DataManipulator import CallType

from pypost.tests import DataUtil

class TestDecorator(DataManipulator):
    def __init__(self, dataManager):
        super().__init__(dataManager)

    @DataManipulator.DataManipulationMethod(inputArguments=[], outputArguments='parameters')
    def sampleParameters(self, numElements):
        return np.ones((numElements, 5))

    @DataManipulator.DataManipulationMethod(inputArguments=[], outputArguments='parameters')
    def sampleParameters2(self, numElements):
        return np.ones((numElements, 5))

class TestDecorator2(TestDecorator):
    def __init__(self, dataManager):
        super().__init__(dataManager)
        self.name1 = 'contexts'
        self.name2 = 'parameters'


    def sampleParameters2(self, numElements):
        return np.ones((numElements, 5)) * 2

    @DataManipulator.DataManipulationMethod(inputArguments=['self.name1'], outputArguments='self.name2')
    def sampleParametersFromContext(self, contexts):
        return np.ones((contexts.shape[0], 5)) * 3 + contexts



class testDataManipulator(unittest.TestCase):

    def test_init(self):
        self.assertRaises(ValueError, DataManipulator, None)

    def test_decorator(self):
        dataManager = DataUtil.createTestManager()
        testDecorator = TestDecorator2(dataManager)

        data = dataManager.getDataObject(10)
        context = np.array(range(0,10))
        context.resize(10,1)
        data.setDataEntry('contexts', ..., context)

        testDecorator.sampleParameters_fromData(data)
        self.assertTrue((data.getDataEntry('parameters') == np.ones((10,5))).all())
        testDecorator.sampleParameters2_fromData(data, slice(0,5))
        self.assertTrue((data.getDataEntry('parameters', slice(0,5)) == np.ones((5,5)) * 2).all())
        self.assertTrue((data.getDataEntry('parameters', slice(5, 10)) == np.ones((5, 5))).all())

        testArray = np.array([[3., 3., 3., 3., 3.],
                              [4., 4., 4., 4., 4.],
                              [5., 5., 5., 5., 5.],
                              [6., 6., 6., 6., 6.],
                              [7., 7., 7., 7., 7.]])

        testArray2 = testDecorator.sampleParametersFromContext_fromData(data, slice(0,5), registerOutput = False)
        self.assertTrue((testArray2 == testArray).all())

        testDecorator.sampleParametersFromContext_fromData(data, slice(0,5))
        self.assertTrue((data.getDataEntry('parameters', slice(0,5)) == testArray).all())

        # Now test using a simpl function as data manipulation function
        @DataManipulationFunction(inputArguments='contexts', outputArguments='parameters')
        def dummyFunction(contexts):
            return np.ones((contexts.shape[0], 5)) * 4 + contexts

        dummyFunction(data)
        self.assertTrue((data.getDataEntry('parameters', slice(0, 5)) == testArray + 1).all())


        @DataManipulationFunction(inputArguments='contexts', outputArguments='parameters')
        def dummyFunction2(contexts):
            return np.ones((contexts.shape[0], 1)) * 4

        self.assertRaises(ValueError, dummyFunction2, data)

if __name__ == '__main__':
    unittest.main()
