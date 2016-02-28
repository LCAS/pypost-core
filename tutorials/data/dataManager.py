import unittest
import sys
import numpy as np

sys.path.append('../../src/')

from data.DataAlias import DataAlias
from data.DataEntry import DataEntry
from data.DataManager import DataManager

'''
In this example we are going to see how data managers work. We will
create a data manager, fill it with some random data and then learn how
to retrieve it.
'''

# Initialization of the manager
# create data managers with 3 hierarchical layers (episodes, steps, subSteps)
dataManager = DataManager('episodes')
subDataManager = DataManager('steps')
subSubDataManager = DataManager('subSteps')

# add data entries to each of the layers
# here we add an entry named 'parameters# with 5 elements in range [-1,1]
dataManager.addDataEntry('parameters', 5, -np.ones(5), np.ones(5))
# here we add an entry named 'context# with 2 elements in range [-1,1]
dataManager.addDataEntry('context', 2, -np.ones(2), np.ones(2))

# so far we have said that an episode is characterized by 5 parameters and
# 2 contexts

# now add a data alias
# subParameters is now an alias for the [1 3 5] dimension of parameters
dataManager.addDataAlias('subParameters', [('parameters', slice(0, 5, 2)),
                                           ('context', ...)])

# do the same with the sub-manager: we have states and actions as data for
# each steps
subDataManager.addDataEntry('states', 1, -np.ones(1), np.ones(1))
subDataManager.addDataEntry('actions', 2, -np.ones(2), np.ones(2))

# ... and the same for the sub-sub-manager
subSubDataManager.addDataEntry('subStates', 1, -np.ones(1), np.ones(1))
subSubDataManager.addDataEntry('subActions', 2, -np.ones(2), np.ones(2))

# now we only need to connect the data managers and finalize them
dataManager.subDataManager = subDataManager
subDataManager.subDataManager = subSubDataManager


# Initialization of the data
# so far we have defined the structure of our data
# now we want to create new data

# here we create new data object with 100 episodes, 10 steps and 5 sub-steps
# (i.e. 5000 substeps in total)
# this method will also finalize the dataManager
myData = dataManager.getDataObject([100, 10, 5])

# we could also have created a data object with 10 episodes, 10 steps and 10
# sub-steps by using a scalar:
# myData = dataManager.getDataObject(10)

# we can also reserve more data storage (i.e. the matrices for all
# necessary data entries are enlarged)
myData.reserveStorage([100, 20, 5])

# the following command accesses all parameters of the first episode
print('parameters: \n', myData.getDataEntry('parameters', 1), '\n\n')

# by setting cloneData to False, references to the data in the data structure
# are returned. Updates in the returned data may influence the data in the
# data structure and in other references with cloneData==False. Nevertheless, it
# is crucial to write all pending changes by using setDataEntry().
print('parameters: \n', myData.getDataEntry('parameters', 1, False), '\n\n')

# and the following command retreives the subActions of all subSteps of the
# first step of the first episode
print('subActions: \n', myData.getDataEntry(['steps', 'subSteps', 'subActions'],
                                            [1, 1, ...]), '\n\n')

# this can also be written as
# in this case, [1, 1] is auto-expanded to [1, 1, ...]
print('the same subActions: \n',
      myData.getDataEntry('subActions', [1, 1]), '\n\n')

# Next, we create some data and write it to "parameters".
# The dimension of parameterData is (10, 5) because we created 100 episodes with
# a 5-dimensional parameter object each
parameterData = np.ones((100, 5))
myData.setDataEntry('parameters', [], parameterData)

# Retrieval of our data
# we can retrieve all our data ...
tempParameters = myData.getDataEntry('parameters', ...);

# ... or use indices to access the hierarchical data structure
# and get all parameters of the first empisode
tempParametersFirstEpisode = myData.getDataEntry('parameters', [1]);

# we can also use the '...# sign to specify that we want to have all elements
# of this layer of the hierarchy this commands returns the first subActions
# of all episodes of the first step. We can specify as many indices as
# there are layers. If an index is not specified, it is assumed to be "...".
tempActions = myData.getDataEntry('subActions', [..., 1, 1]);

# update the data
tempActions[:, :] = 42
tempActions[90, :] = 1
tempActions[90, 1] = 2
tempActions[91, 0] = 3
tempActions[91, 1] = 4

# indicing also works for the setting functions
myData.setDataEntry('subActions', [..., 1, 1], tempActions);

# retrieve the data again
print('Updated subActions:\n', myData.getDataEntry('subActions', [..., 1, 1]), '\n')


# We can also access the last element with negative indices.
print('Both data entries should be the same:',
    (myData.getDataEntry('actions', [..., -1]) == myData.getDataEntry(
        'actions', [..., 19])).all())

print('Both data entries should be the same:',
    (myData.getDataEntry('subActions', [..., 1, -1]) == myData.getDataEntry(
    'subActions', [..., 1, 4])).all())

print('\nThats it, the show is over...');
