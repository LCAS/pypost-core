from pypost.data import DataManager
from pypost.mappings import Mapping

#define our mapping class. A mapping is a callable object, where the call function is implemented by the MappingMethod decorator

class DummyMapping(Mapping):

    def __init__(self, dataManager):
        Mapping.__init__(self, dataManager, inputVariables=['X'], outputVariables='X')

    @Mapping.MappingMethod()
    def computeSomething(self, X):
        return X + 1


# Create a dataManager that can handle the input (X) and output (Y) of a 1 dimensional
# function
dataManager = DataManager('values')
dataManager.addDataEntry('X', 2)

data = dataManager.getDataObject([10])

mapping = DummyMapping(dataManager)

print(data[...].X)

data[...] >> mapping
print(data[...].X)

data[...] >> mapping
print(data[...].X)

data[slice(0,5)] >> mapping
print(data[...].X)

