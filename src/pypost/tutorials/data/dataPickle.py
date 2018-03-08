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
subDataManager = DataManager('steps')

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
myData = dataManager.createDataObject([100, 10])

# show all states (1000)


myData[...].states = np.random.normal(0, 1, myData[...].states.shape)

import pickle

pickle.dump(myData, open('testPickle.pkl', 'wb'))

newData = pickle.load(open('testPickle.pkl', 'rb'))

assert(np.sum(np.abs(myData[...].states - newData[...].states)) == 0)
