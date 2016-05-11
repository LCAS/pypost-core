import sys
import numpy as np

from pypost.data.DataManager import DataManager
from pypost.MappingTestClass import MappingTestClass

'''
The Mapping class represents the base class of all mathematical
representations (functions, distributions...) that map an input (possibly an empty set) to one or more output
values. The mapping class extends the data manipulator interface. A mapping has
predefined input and output variables. If we add a mapping function with
the method addMappingFunction, a new data manipulation function is created where
the input and output variables are already predefined according to the
input and output variables defined by the mapping. The output variables
can be changed though for each mapping function that we define by the
optional arguments of the addMappingFunction method.
'''

# Create a dataManager that can handle the input (X) and output (Y) of a 1 dimensional
# function
dataManager = DataManager('values')
dataManager.addDataEntry('X', 1)
dataManager.addDataEntry('Y', 1)

data = dataManager.getDataObject([11])

functionCollection = MappingTestClass(dataManager)
xData = np.linspace(-np.pi, np.pi, 11)[np.newaxis, :].T
print(xData)

data.setDataEntry('X', ..., xData)
print(data.getDataEntry('X', ...))

functionCollection.callDataFunction('getFunctionValue', data)

newY = data.getDataEntry('Y', ...)
print(newY)

dY = functionCollection.callDataFunctionOutput('getFunctionGradient', data)
print(dY[0][0])
