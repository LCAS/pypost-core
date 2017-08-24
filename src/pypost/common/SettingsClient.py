from pypost.common import SettingsManager, DataPrinter

class SettingsClient():
    '''Base class for all IASObjects.

    Implements basic functionality for registering properties of an object in the global parameter pool.
    '''

    def __init__(self, namespace=None):
        '''Creates a new object.
        '''
        self.settingsClientName = SettingsManager.getNextClientName()
        self.settings = SettingsManager.getDefaultSettings()

        self.suffixString = self.settings.getSuffixString()
        '''
        Get a unique name for this client
        '''
        self._localPropertyMap = {}


    def linkPropertyToSettings(self, clientPropName, settingsPropName = None, takeValueFromClient = False):
        '''Registers the property 'clientPropName' of the object into the parameter pool.

        The parameter 'settingsPropName' sets the global name of the
        property used in the parameter pool (default is the same name
        as the internal name used for the class). The parameter
        settings specifies the parameter pool where we want to
        register the property. Default is the global parameter pool.
        If a property is linked and the property already exists in the
        parameter pool, the value from the parameter pool is used to
        overwrite the value of the property of the object. If the
        property does not exist in the parameter pool, it property is
        registered in the parameter pool. The value in the parameter
        pool is in this case set to the current value of the local
        property.
        NOTE: ALL properties that are linked must be declared as
        'AbortSet' and 'SetObservable'!

        :param clientPropName: Name of the property as defined in the client
        :param settingsPropName: Name of the property as defined in the settings
        :param settings: The Settings to be used
        '''
        if settingsPropName is None:
            settingsPropName = clientPropName


        self.settings.linkProperty(self, clientPropName, self.getNameWithSuffix(settingsPropName), takeValueFromClient = takeValueFromClient)
        self._localPropertyMap[clientPropName] = settingsPropName

    def getNameWithSuffix(self, name):
        if self.suffixString:
            if isinstance(name, list):
                for i in range(0, len(name)):
                    localName = name[i]
                    if not (len(localName) > len(self.suffixString) and localName[-len(self.suffixString) + 1:] == self.suffixString):
                        name[i] = localName  + self.suffixString
            else:
                if not (len(name) > len(self.suffixString) and name[-len(self.suffixString) + 1:] == self.suffixString):
                    name = name + self.suffixString
        return name

    def printProperties(self):
        '''Print the properties
        '''
        for cn in self._localPropertyMap.keys():
            DataPrinter.printData(cn + ': ' + str(self.getVar(cn)))

    def getVar(self, varName):
        '''Returns the value of the attribute with the given name.

        :param varName: Name of the property
        '''
        return getattr(self, varName)

    def setVar(self, varName, value):
        '''Sets the value of the attribute with the given name.

        :param varName: Name of the property
        :param value: The new value
        '''
        setattr(self, varName, value)

    def setIfNotEmpty(self, prop, val):

        if self.getVar(prop) is None:
            self.setVar(prop, val)
            self.settings.setProperty(self._localPropertyMap[prop], val)
