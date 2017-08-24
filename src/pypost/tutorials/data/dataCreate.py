from pypost.data import DataManager
from pypost.data import DataManagerTimeSeries
from pypost.data import DataType


import numpy as np
'''
In this example we are going to see how to use aliases.
'''

# create data manager
dataManager = DataManager('episodes')
subDataManager = DataManagerTimeSeries('steps')

subDataManager.addDataEntry('states', 2)
subDataManager.addDataEntry('actions', 3, dataType=DataType.discrete)


dataManager.subDataManager = subDataManager

# create data object with 10 episodes
data = dataManager.createDataObject(10)

# fill episodes. we want to use a different number of timesteps for each episode

for i in range(0,10):
    numTimeSteps = i + 5
    data.reserveStorage(numTimeSteps, [i])

    print('Size of states matrix: ', data[i].states.shape)

    #fill in some dummy actions
    data[i].allStates = np.array(np.vstack((range(0,numTimeSteps + 1), range(0,numTimeSteps + 1)))).transpose()
    data[i].actions = np.ones((numTimeSteps, 3), dtype=int) * i * 2

# we can also use vectors and numericals (in case of scalar values) in the setting functions
data[i].actions = np.ones((3,), dtype=int) * - 5


# we can now access single trajectories
print(data[2].states)

# all trajectories concatenaded
print(data[...].states)

# all trajectories concatenaded horizontally. We get nan values for timesteps in episodes that do not exist
print(data[...].states__T)
# This matrix is 14 (max timeSteps) x (10 episodes * 2 dimensions)
print(data[...].states__T.shape)

# access all states of a single time step. Episodes that are shorter then the specified time-step are ignored
print(data[:, 10].states)
# only 4 episodes have more then 10 time steps
print(data[:, 10].states.shape)
