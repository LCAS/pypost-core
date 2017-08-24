import numpy as np
import time
from pypost.data import DataManager
from pypost.data import DataManagerTimeSeries

'''
In this example we are going to see how data managers work. We will
create a data manager, fill it with some random data and then learn how
to retrieve it.
'''

# Initialization of the manager
# create data managers with 3 hierarchical layers (episodes, steps, subSteps)
dataManager = DataManager('episodes')
subDataManager = DataManagerTimeSeries('steps')

# do the same with the sub-manager: we have states and actions as data for
# each steps
subDataManager.addDataEntry('states', (5,5), -np.ones((5,5)), np.ones((5,5)))
subDataManager.addDataEntry('actions', 1, -np.ones(1), np.ones(1))

# now we only need to connect the data managers and finalize them
dataManager.subDataManager = subDataManager

# Initialization of the data
# so far we have defined the structure of our data
# now we want to create new data


numTimeSteps = 1000

# here we create new data object with 1 episodes, 10000 steps
# this method will also finalize the dataManager
myData = dataManager.createDataObject([10, numTimeSteps])

# for time series, we have special aliases for accesing the next element, previous element and all elements

# Fill all states matrices

for j in range(0,10):
    for i in range(0, numTimeSteps):
        myData[j,i].states = np.ones((5,5)) * i + j * 1000


t0 = time.time()
print('States (...,1):', myData[..., 1].states)
print('Current shape (...,1):', myData[..., [1]].states.shape)
t1 = time.time()
print('Timing:', t0 - t1)

t0 = time.time()
print('States (1,...):', myData[1, ...].states)
print('Current shape (1,...):', myData[1, ...].states.shape)
t1 = time.time()
print('Timing:', t0 - t1)


t0 = time.time()
print('States ([1,2,3],...):', myData[[1,2,3], ...].states)
print('Current shape ([1,2,3],...):', myData[[1,2,3], ...].states.shape)
t1 = time.time()
print('Timing:', t0 - t1)
