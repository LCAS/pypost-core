from pypost.common import SettingsManager
from pypost.common import SettingsClient


settings = SettingsManager.getDefaultSettings()

settings.registerProperty('dummyValue', 1)
print('Settings.dummyValue:', settings.dummyValue)


class DummyClass(SettingsClient):
    def __init__(self):
        SettingsClient.__init__(self)

        self.myDummyVariable = 3

        # link to settings in parameter pool. Global name is dummy value
        # If the parameter does not exist, it is registered with the current property value
        self.linkPropertyToSettings('myDummyVariable', globalName='dummyValue')

    def printDummy(self):
        print('Dummy:', self.myDummyVariable)


# dummy instance takes
dummyInstance = DummyClass()

# Value should now be 1.0 (taken from the parameter pool)
dummyInstance.printDummy()

settings.dummyValue = 4.0
# Value should now be 4.0 (taken from the parameter pool)
dummyInstance.printDummy()

# Print all properties
settings.printProperties()

#It does, however, not work the other way round
dummyInstance.myDummyVariable = 2
# Print all properties, settings is not changed!
settings.printProperties()

