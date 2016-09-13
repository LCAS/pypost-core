import numpy as np

from pypost.data import DataManager

'''
In this example we are going to see how data managers work. We will
create a data manager, fill it with some random data and then learn how
to retrieve it.
'''

# Initialization of the manager
# create data managers with 3 hierarchical layers (episodes, steps, subSteps)
dataManager = DataManager('episodes')
subDataManager = DataManager('steps', isTimeSeries=True)

# add data entries to each of the layers
# here we add an entry named 'parameters' with 5 elements in range [-2,2]
dataManager.addDataEntry('parameters', 5, -2*np.ones(5), 2*np.ones(5))
# here we add an entry named 'context' with 2 elements in range [-1,1]
# (this is the default for minRange and maxRange)
dataManager.addDataEntry('context', 2)

# do the same with the sub-manager: we have states and actions as data for
# each steps
subDataManager.addDataEntry('states', 1, -np.ones(1), np.ones(1))
subDataManager.addDataEntry('actions', 2, -np.ones(2), np.ones(2))

# now we only need to connect the data managers and finalize them
dataManager.subDataManager = subDataManager

# Initialization of the data
# so far we have defined the structure of our data
# now we want to create new data

# here we create new data object with 100 episodes, 10 steps
# this method will also finalize the dataManager
myData = dataManager.getDataObject([1, 10])

# for time series, we have special aliases for accesing the next element, previous element and all elements

# Fill all states with series
series = np.array(range(0,11))
series.resize(11,1)
myData[...].allStates = series
print('Current states:', myData[...].states)
print('Next states:', myData[...].nextStates)
print('Previous states:', myData[..., slice(0,10)].lastStates)
print('All states:', myData[...].allStates)

