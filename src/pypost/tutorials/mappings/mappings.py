from pypost.data import DataManager
from pypost.mappings import DataManipulator
from pypost.mappings import Mapping
import numpy as np

#define our mapping class. A mapping is a callable object, where the call function is implemented by the MappingMethod decorator

class DummyMapping(Mapping):

    def __init__(self, dataManager):
        Mapping.__init__(self, dataManager, inputVariables=['X'], outputVariables='X')

    @Mapping.MappingMethod()
    def computeSomething(self, X):
        return X + 1

    @DataManipulator.DataMethod(inputArguments=[], outputArguments=['X'], takesNumElements=True)
    def reset(self, numElements):
        return np.zeros((numElements,2))

# Create a dataManager that can handle the input (X) and output (Y) of a 1 dimensional
# function
dataManager = DataManager('values')
dataManager.addDataEntry('X', 2)

data = dataManager.createDataObject([10])

mapping = DummyMapping(dataManager)

print(data[...].X)

# apply mapping
data[...] >> mapping >> data
print(data[...].X)

mapping.reset >> data


# Applying the >> to the mapping and writing the result back to data. Using the >> operator for the second operation returns the data object
data[slice(0,5)] >> mapping >> data
print(data[...].X)

# Applying the >> to the mapping and writing the result back to data. Using the >= operator for the second operation returns the resulting matrices
temp = data[...] >> mapping >= data
print(data[...].X, temp)


