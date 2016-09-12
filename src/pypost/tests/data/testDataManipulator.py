import unittest
import numpy as np
from pypost.data.DataManipulator import DataManipulator
from pypost.data.DataManipulator import DataFunction

from pypost.tests import DataUtil

class TestDecorator(DataManipulator):
    def __init__(self, dataManager):
        super().__init__(dataManager)

    @DataManipulator.DataMethod(inputArguments=[], outputArguments='parameters')
    def sampleParameters(self, numElements):
        return np.ones((numElements, 5))

    @DataManipulator.DataMethod(inputArguments=[], outputArguments='parameters')
    def sampleParameters2(self, numElements):
        return np.ones((numElements, 5))

class TestDecorator2(TestDecorator):
    def __init__(self, dataManager, name1):
        super().__init__(dataManager)
        self.name1 = name1
        self.name2 = 'parameters'


    def sampleParameters2(self, numElements):
        return np.ones((numElements, 5)) * 2

    @DataManipulator.DataMethod(inputArguments=['self.name1'], outputArguments='self.name2')
    def sampleParametersFromContext(self, contexts):
        return np.ones((contexts.shape[0], 5)) * 3 + contexts



class testDataManipulator(unittest.TestCase):

    def test_init(self):
        self.assertRaises(ValueError, DataManipulator, None)

    def test_decorator_operator(self):
        dataManager = DataUtil.createTestManager()

        testDecorator = TestDecorator2(dataManager, 'contexts')
        testDecorator2 = TestDecorator2(dataManager, 'parameters')

        data = dataManager.getDataObject(10)
        context = np.array(range(0,10))
        context.resize(10,1)
        data.setDataEntry('contexts', ..., context)

        data >> testDecorator.sampleParameters

        self.assertTrue((data.getDataEntry('parameters') == np.ones((10,5))).all())
        data[slice(0,5)] >> testDecorator.sampleParameters2

        self.assertTrue((data.getDataEntry('parameters', slice(0,5)) == np.ones((5,5)) * 2).all())
        self.assertTrue((data.getDataEntry('parameters', slice(5, 10)) == np.ones((5, 5))).all())

        testArray = np.array([[3., 3., 3., 3., 3.],
                              [4., 4., 4., 4., 4.],
                              [5., 5., 5., 5., 5.],
                              [6., 6., 6., 6., 6.],
                              [7., 7., 7., 7., 7.]])

        testArray2 = data[slice(0,5)] > testDecorator.sampleParametersFromContext
        self.assertTrue((testArray2 == testArray).all())

        data[slice(0, 5)] >> testDecorator.sampleParametersFromContext
        self.assertTrue((data.getDataEntry('parameters', slice(0,5)) == testArray).all())

        # Now test using a simpl function as data manipulation function
        @DataFunction(inputArguments='contexts', outputArguments='parameters')
        def dummyFunction(contexts):
            return np.ones((contexts.shape[0], 5)) * 4 + contexts

        data[:] >> dummyFunction
        self.assertTrue((data.getDataEntry('parameters', slice(0, 5)) == testArray + 1).all())


        @DataFunction(inputArguments='contexts', outputArguments='parameters')
        def dummyFunction2(contexts):
            return np.ones((contexts.shape[0], 1)) * 4

        self.assertRaises(ValueError, data.__rshift__, dummyFunction2)


if __name__ == '__main__':
    unittest.main()
