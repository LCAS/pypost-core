import numpy as np

from pypost.data import DataManager
from pypost.common.SettingsManager import *


settings = getDefaultSettings()

settings.setProperty('optionalEntry', np.array([[-2, -2]]))
settings.setProperty('optionalEntry2', 1)

dataManager = DataManager('episodes')
# Create optional entry where default is not to use it
dataManager.addOptionalDataEntry('optionalEntry', False, 2, np.array([[-1, -1]]), np.array([[5, 5]]))
# Create optional entry where default is not to use, but we overwrite this default before
settings.setProperty('useOptionalEntry2', True)
dataManager.addOptionalDataEntry('optionalEntry2', False, 1, np.array([[-1]]), np.array([[5]]))

data = dataManager.createDataObject(3)


# Optional entry is now [-2 -2]
print('Optional Entry\n', data[...].optionalEntry, '\n\n')


dataManager.settings.setProperty('optionalEntry', np.array([[-5, -5]]))
# Optional entry is now [-5 -5]
print('Optional Entry\n', data[...].optionalEntry, '\n\n')

# We can not put data in optional entry
try:
    data[...].optionalEntry = np.zeros((3, 2))
except ValueError as error:
    pass

# 2nd entry is activated, does not follow settings but can be set
print('Optional2 Entry\n', data[...].optionalEntry2, '\n\n')
settings.setProperty('optionalEntry2', -10)
print('Optional2 Entry\n', data[...].optionalEntry2, '\n\n')

data[...].optionalEntry2 = np.array([[1],[2],[3]])
print('Optional2 Entry\n', data[...].optionalEntry2, '\n\n')

