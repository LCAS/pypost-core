from pypost.data import DataManager
import time
'''
In this example we are going to see how to use aliases.
'''

# create data manager
dataManager = DataManager('episodes')

# add data entries
dataManager.addDataEntry('parameters', 5)

dataManager.addDataEntry('contexts', 5)

# add an alias
# parameterAlias points to the first two dimensions of parameters
dataManager.addDataAlias('parameterAlias', [('parameters',  slice(0, 2))])

# it's also possible to create an alias that points to another alias
# 'aliasAlias' will now be the aquivalent to 'parameters'
dataManager.addDataAlias('aliasAlias', [('parameterAlias', ...), ('contexts', slice(2, 5))])

dataManager.addDataAlias('parametersAliasVertical', [('parameters',  slice(0, 2)), ('parameters',  slice(2, 4))], useConcatVertical=True)


# create the data object
myData = dataManager.createDataObject([3])

# set the entries of the 'parameters' entry. This will also affect the alias
# that points to 'parameters'
parameters = myData[...].parameters
parameters[:] = [1, 2, 3, 4, 5]
myData[...].parameters = parameters

# print all parameters
print('initial parameters\n', parameters, '\n\n')

# print all parameters again (using the alias)
aliasAlias = myData[...].aliasAlias
print('initial aliasAlias\n', aliasAlias, '\n\n')

# update the parameters via the alias
aliasAlias[1] = [5, 5, 3, 5, 5]

# store the updated parameters
myData[1].aliasAlias = aliasAlias[1]

# print all parameters one more time
print('updated parameters\n', myData[...].parameters, '\n\n')

# print all parameters again (using the alias)
print('updated context\n', myData[...].contexts, '\n\n')

# print all parameters again (using the alias)
print('updated aliasAlias\n', myData[...].aliasAlias, '\n\n')

# test vertical alignment for alias
print('vertical Alias\n', myData[...].parametersAliasVertical, '\n\n')

# test vertical alignment for alias
myData[...].parametersAliasVertical = myData[...].parametersAliasVertical * 2

print('vertical Alias after resetting values\n', myData[...].parametersAliasVertical, '\n\n')
print('Original Parameters after resetting values\n', myData[...].parameters, '\n\n')

print('Num Dim Vertical Parameters\n', dataManager.getNumDimensions('parametersAliasVertical'), '\n\n')
