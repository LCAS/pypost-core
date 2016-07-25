import unittest
import sys
import numpy as np

from pypost.data.DataAlias import DataAlias
from pypost.data.DataEntry import DataEntry
from pypost.data.DataManager import DataManager

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

# it's also possible to create an alias that points to another alias
# 'aliasAlias' will now be the aquivalent to 'parameters'
dataManager.addDataAlias('aliasAlias',
                         [('parameterAlias', ...),
                          ('parameters', slice(2, 5))])


# create the data object
myData = dataManager.getDataObject([3, 5, 10])

# set the entries of the 'parameters' entry. This will also affect the alias
# that points to 'parameters'
parameters = myData.getDataEntry('parameters')
parameters[:] = [1, 2, 3, 4, 5]
myData.setDataEntry('parameters', [], parameters)

# print all parameters
print('inital parameters\n', parameters, '\n\n')

# print all parameters again (using the alias)
aliasAlias = myData.getDataEntry('aliasAlias')
print('inital aliasAlias\n', aliasAlias, '\n\n')

# update the parameters via the alias
aliasAlias[1] = [5, 5, 3, 5, 5]

# store the updated parameters
myData.setDataEntry('aliasAlias', [], aliasAlias)

# print all parameters one more time
print('updated parameters\n', myData.getDataEntry('parameters'), '\n\n')

# print all parameters again (using the alias)
print('updted aliasAlias\n', myData.getDataEntry('aliasAlias'), '\n\n')
