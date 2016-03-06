from collections import namedtuple
from common import DataPrinter


class Settings():
    # TODO: revise comment
    '''
    The Settings class implements a parameter pool where we can link
    properties of several objects. The value of the linked properties
    will be set to the value set in the parameter pool. If we link a
    property that is so far not registered in the parameter pool, the
    property name is registered with the current value of the property
    set in the parameter pool. Important functions of this class for the
    user are Settings.registerProperty, Settings.setProperty,
    Settings.getProperty and Settings.hasProperty. The class also offers
    the functionality to create several parameter pools (for example if
    we want to use different parameters for different instances of the
    same class). However, typically just a single, global parameter pool
    is used. The global parameter pool can be accessed by calling the
    empty constructor, i.e., Common.Settings().

    It is recommended to access the variables directly via the getter and setter instead of linking it, if you care about performance.

    :change: The notation 'id' has been replaced with 'name' due to name conflicts
    :change: isSameSettings() has been replaced with getDifferentProperties()
    :change: getPropertyNames() and getNumProperties() are not implemented
    '''

    propertyInfo= namedtuple('PropertyInfo', ['value', 'clients'])
    '''
    Tuple storing the name of a property and a list of ClientInfo
    '''
    clientInfo = namedtuple('ClientInfo', ['client', 'clientPropName'])
    '''
    Tuple storing a reference to the client and the name of the property in the client
    '''

    def __init__(self, name):
        '''Creates a new Settings object with the given name.

        :param name: The name of the Settings
        :change: Just creates an object and doesn't care about existing instances in the SettingsManager. For getting the default settings use: SettingsManager.getDefaultSettings()
        '''
        self.name = name
        '''
        Name of the Settings
        '''
        self._properties = {}
        '''
        Contains the properties that are stored in the pool and the corresponding clients.
        It should be structured after the following pattern: {propertyName: Property(value=<value of the property>, ClientInfo(client=<client object>, clientPropName=<property name in client>)}
        Property and ClientInfo are namedtuples
        '''
    def clean(self):
        '''Removes all properties in this pool.
        '''
        self._properties = {}

    def removeClients(self):
        '''Unregisters all registered clients.
        '''
        for p in self._properties.values():
            del p.clients[:]

    def registerProperty(self, propName, value):
        '''Registers a the specified property.

        :param propName: Name of the property in the settings
        :param value: value of the property
        '''
        if propName in self._properties:
            self._properties[propName] = self.propertyInfo(value, self._properties[propName].clients)
        else:
            self._properties[propName] = self.propertyInfo(value, [])

            # NOTE: Use properties for changes?

    def unregisterProperty(self, propName):
        '''Unregisters the property with the given name.

        :param propName: Name of the property to unregister
        '''
        if propName in self._properties:
            del self._properties[propName]

    def linkProperty(self, client, clientPropName, settingsPropName):
        '''Links a property in the settings with the specified property of the given client. If the property isn't already present in the settings, it will be registered.

        :param client: The client owning the property to be linked.
        :param clientPropName: The property's name as defined in the client
        :param settingsPropName: The property's name as (it should be) defined in the settings
        '''
        if settingsPropName in self._properties:
            client.globalProperties[clientPropName] = self._properties[settingsPropName].value
        else:
            self.registerProperty(settingsPropName, client.globalProperties[clientPropName])

        self._properties[settingsPropName].clients.append(self.clientInfo(client, clientPropName))

    def getProperty(self, propName):
        '''Returns the value of the property that is registered in the parameter pool with the given name.

        :param propName: Name of the property to return
        :returns: the value of the specified property
        '''
        if propName in self._properties:
            return self._properties[propName].value

    def getProperties(self):
        '''Returns a dictionary containing the properties' names (as keys) and their values.

        :returns: Dictionary containing the properties
        '''
        return {propName: prop.value for (propName, prop) in self._properties.items()}

    def setProperty(self, propName, value):
        '''Sets the property with the given name to the specified value.
        If the parameter with the propName isn't existent in this parameter pool, it will be registered.

        :param propName: Name of the property to set
        :param value: new value of the property
        '''
        isRegistered = propName in self._properties
        self.registerProperty(propName, value)
        if isRegistered:
            self.informClients(propName)

    def setIfEmpty(self, propName, value):
        '''Sets the property with the given name only if it isn't already registered.

        :param propName: Name of the property to set
        :param value: new value of the property
        '''
        if propName not in self._properties:
            self.setProperty(propName, value)

    def setProperties(self, properties):
        '''Sets multiple properties.

        :param properties: A dictionary containing the names of the properties
                           as keys and the values being the values of each
                           property
        '''
        for p, v in properties.items():
            self.setProperty(p, v)

    def hasValue(self, propertyName, value):
        '''Checks if a property with the given name and value exists.

        :param propertyName: Name of the property to check
        :param value: value to check
        :returns: True, if a property with the given name and value exists;
                  otherwise: False
        '''
        return self._properties[propertyName].value == value

    def hasProperty(self, propName):
        '''Checks if there is a property registered with the given name.

        :param propName: Name of the property to check
        :returns: True, if there is a property registered with the given name;
                  otherwise: False
        '''
        return propName in self._properties

    def copyProperties(self, settings):
        '''Copies all properties from another Settings object to the parameter pool. Clients won't be deleted.

        :param settings: The Settings object from which the parameters shall be copied.
        '''
        self.setProperties(settings.getProperties())

    def getDifferentProperties(self, otherSettings):
        '''Returns the names of the properties differing from those in the given Settings object.

        :param otherSettings: The settings to compare with
        :returns: The names of the properties differing from those in the given Settings object

        :change: This should replace isSameSettings
        '''
        return {n for n, v in self._properties.items() if otherSettings.getProperty(n) != v.value}

    def setToClients(self):
        '''Updates all linked properties of all clients.
        '''
        for p in self._properties.keys():
            self.informClients(p)

    def informClients(self, propName):
        '''Updates the client's property that is linked to the property with the given name.

        :param propName: Name of the property in the pool
        '''
        if propName in self._properties:
            for c, n in self._properties[propName].clients:
                c.globalProperties[n] = self._properties[propName].value

    def printProperties(self):
        '''Prints the properties
        '''
        DataPrinter.printData(self.getProperties())
