from pypost.data import DataManager
from pypost.mappings import DataManipulator
from pypost.mappings import additional_inputs
from pypost.mappings import CallType


#define our manipulator. A manipulator can define several data manipulation methods with the DataMethod decoration interface

class DummyManipulator(DataManipulator):

    def __init__(self, dataManager):
        DataManipulator.__init__(self, dataManager)
        self.input1 = 'X'
        self.input2 = 'Y'

    @DataManipulator.DataMethod(inputArguments=['X'], outputArguments=['Y'])
    def computeSomething(self, X):
        print('computeSomething got called with!', X)
        return X + 1

    @DataManipulator.DataMethod(inputArguments=['self.input1'], outputArguments=['Z'], callType = CallType.SINGLE_SAMPLE)
    def computeSomethingSequential(self, X):
        print('computeSomethingSequential got called with!', X)
        return X + 2

    @DataManipulator.DataMethod(inputArguments=['self.input1'], outputArguments=[], additionalArguments=['dummy'])
    def computeSomethingAdditional(self, X, dummy):
        print('computeSomethingSequential got called with:', X + ' and ' + dummy)
        return


# Create a dataManager that can handle the input (X) and output (Y) of a 1 dimensional
# function
dataManager = DataManager('values')
dataManager.addDataEntry('X', 2)
dataManager.addDataEntry('Y', 2)
dataManager.addDataEntry('Z', 2)

data = dataManager.createDataObject([3])

manipulator = DummyManipulator(dataManager)

print(data[...].X)

# The >> operator calls the data manipulator, stores the result in the data structure and returns the new data structure
data[...] >> manipulator.computeSomething >> data
print('data.Y:', data[...].Y)

data[...] >> manipulator.computeSomethingSequential >> data
print('data.Z:', data[...].Z)

# The >= operator calls the data manipulator, stores the result in the data structure and returns the result of evaluating the data manipulator

Y = data[...] >> manipulator.computeSomething >= data

manipulator.listManipulationFunctions()

# Test manipulator with additional arguments that are not in the data object
# Not supported at the moment!
#data[...] >> (additional_inputs(5) >> manipulator.computeSomethingAdditional)
