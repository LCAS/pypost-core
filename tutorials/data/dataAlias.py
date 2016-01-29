import unittest
import sys
import numpy as np

sys.path.append('../../src/')

from data.DataAlias import DataAlias
from data.DataEntry import DataEntry
from data.DataManager import DataManager

'''
In this example we are going to see how to use aliases.
'''

# create data manager
dataManager = DataManager('episodes')

# add data entries
dataManager.addDataEntry('parameters', 5)
dataManager.addDataEntry('context', 5)

# add an alias
# parameterAlias points to the first two dimensions of parameters
dataManager.addDataAlias('parameterAlias', [('parameters',
                                             slice(0, 2))])

# twoAlias is the concatenation of the first two dimensions of parameters
# and the third, fourth and fifth entry of context
dataManager.addDataAlias('twoAlias',
                         [('parameters', slice(0, 2)),
                          ('context', slice(2, 5))])

# Creating new data object
myData = dataManager.getDataObject([10, 5, 1])


myData.dataStructure['parameters'][:] = np.ones(5)
myData.dataStructure['context'][:] = np.ones(5) * 2





















paramAlias = myData.dataStructure['parameterAlias']
paramAlias[:] = np.ones(2) * 3
paramAlias[0][1] = 10
myData.dataStructure['parameterAlias'] = paramAlias

self.assertEqual(myData.dataStructure['parameters'][0][1], 10)
self.assertEqual(myData.dataStructure['parameters'][0][2], 1)
self.assertEqual(myData.dataStructure['parameters'][3][1], 3)
self.assertEqual(myData.dataStructure['parameters'][5][3], 1)

twoAlias = myData.dataStructure['twoAlias']
twoAlias[4] = np.ones(5) * 4
twoAlias[5] = np.ones(5) * 5
twoAlias[6] = np.ones(5) * 6
twoAlias[-1] = np.ones(5) * 9

myData.dataStructure['twoAlias'] = twoAlias

self.assertEqual(myData.dataStructure['twoAlias'][0][3], 2)
self.assertEqual(myData.dataStructure['twoAlias'][-1][3], 9)
self.assertEqual(myData.dataStructure['twoAlias'][4][2], 4)
self.assertEqual(myData.dataStructure['twoAlias'][5][2], 5)
self.assertEqual(myData.dataStructure['parameters'][0][0], 3)
self.assertEqual(myData.dataStructure['parameters'][0][1], 10)
self.assertEqual(myData.dataStructure['parameters'][0][2], 1)
self.assertEqual(myData.dataStructure['parameters'][4][2], 1)
self.assertEqual(myData.dataStructure['parameters'][5][2], 1)
self.assertEqual(myData.dataStructure['context'][1][3], 2)
self.assertEqual(myData.dataStructure['context'][6][3], 6)
self.assertEqual(myData.dataStructure['context'][-1][3], 9)
self.assertEqual(myData.dataStructure['context'][4][0], 2)
self.assertEqual(myData.dataStructure['context'][5][1], 2)
self.assertEqual(myData.dataStructure['context'][4][2], 4)
self.assertEqual(myData.dataStructure['context'][5][2], 5)
