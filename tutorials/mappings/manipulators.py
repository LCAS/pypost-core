from pypost.data import DataManager
from pypost.data import DataManipulator
from pypost.data import CallType


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

    @DataManipulator.DataMethod(inputArguments=['X'], outputArguments=['Z'], callType = CallType.SINGLE_SAMPLE)
    def computeSomethingSequential(self, X):
        print('computeSomethingSequential got called with!', X)
        return X + 2



# Create a dataManager that can handle the input (X) and output (Y) of a 1 dimensional
# function
dataManager = DataManager('values')
dataManager.addDataEntry('X', 2)
dataManager.addDataEntry('Y', 2)
dataManager.addDataEntry('Z', 2)

data = dataManager.getDataObject([3])

mapping = DummyManipulator(dataManager)

print(data[...].X)

data[...] >> mapping.computeSomething
print('data.Y:', data[...].Y)

data[...] >> mapping.computeSomethingSequential
print('data.Z:', data[...].Z)


