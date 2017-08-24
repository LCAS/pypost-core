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
subDataManager.addDataEntry('states', 5, -np.ones(5), np.ones(5))
subDataManager.addDataEntry('actions', 1, -np.ones(1), np.ones(1))
subDataManager.addDataWindowAlias('historyStates', [('states', ...)], -3, 1, dropBoundarySamples=False)

# now we only need to connect the data managers and finalize them
dataManager.subDataManager = subDataManager

# Initialization of the data
# so far we have defined the structure of our data
# now we want to create new data


numTimeSteps = 1000

# here we create new data object with 1 episodes, 10000 steps
# this method will also finalize the dataManager
myData = dataManager.createDataObject([100, numTimeSteps])

# for time series, we have special aliases for accesing the next element, previous element and all elements

# Fill all states with series
allStates = np.zeros((numTimeSteps + 1, 5))

allStates[:,0] = np.array(range(0, numTimeSteps + 1)).transpose()
allStates[:,1] = np.array(range(0, numTimeSteps + 1)).transpose() + 0.1
allStates[:,2] = np.array(range(0, numTimeSteps + 1)).transpose() + 0.2
allStates[:,3] = np.array(range(0, numTimeSteps + 1)).transpose() + 0.3
allStates[:,4] = np.array(range(0, numTimeSteps + 1)).transpose() + 0.4

for i in range(0,100):
    myData[i].allStates = allStates

t0 = time.time()
print('Current states:', myData[...].states)
t1 = time.time()
print('Timing:', t0 - t1)

t0 = time.time()
print('Next states:', myData[...].nextStates)
t1 = time.time()
print('Timing:', t0 - t1)

t0 = time.time()
print('Previous states:', myData[..., slice(0,10)].lastStates)
t1 = time.time()
print('Timing:', t0 - t1)

t0 = time.time()
print('All states:', myData[...].allStates)
t1 = time.time()
print('Timing:', t0 - t1)

t0 = time.time()
print('History states:', myData[...].historyStates.shape)
t1 = time.time()
print('Timing:', t0 - t1)

t0 = time.time()
# get history states for each episode
for i in range(0,100):
    print('History states ', i,' shape:', myData[i].historyStates.shape)
t1 = time.time()
print('Timing:', t0 - t1)

print('History Dimensions:', dataManager.getNumDimensions('historyStates'))