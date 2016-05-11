'''
This module maintains the individual Settings objects.

:change: The notation 'id' has been replaced with 'name' due to name conflicts
'''
from pypost.common.Settings import Settings
from pipes import SOURCE

collection = {}
'''
Contains the Settings objects and their names as keys
'''
debugMode = False
'''
Flag for debug mode
'''
defaultNames = ['default']
'''
Names of default settings.
This should never be empty.
'''
lastClientId = 0
'''
The ID number of the lastly created client.
Clients are numbered in the order in which they where created starting with 1.
:change: Now stores the last ID instead of the next -> changed name.
'''

def activateDebugMode():
    '''Activates the debug mode.
    '''
    global debugMode
    debugMode = True

def deactivateDebugMode():
    '''Deactivates the ()debug mode.
    '''
    global debugMode
    debugMode = False

def inDebugMode():
    '''Returns True, when in debug mode; otherwise False.

    :returns: True, when in debug mode; otherwise False
    '''
    return debugMode

def getDefaultSettings():
    '''Returns the default Settings.

    If there are no default Settings, they will be created.

    :returns: The default Settings
    '''

    default = getSettings(getDefaultName())
    if default is None:
        default = Settings(getDefaultName())
        setSettings(default)
    return default

def pushDefaultName(name):
    '''Adds a new name of default Settings.

    :param name: The name to push
    '''
    global defaultNames
    defaultNames.append(name)

def getRootName():
    '''Returns the name of the root Settings.

    :returns: Name of the root Settings
    '''
    return defaultNames[0]

def getDefaultName():
    '''Returns the name of the default Settings

    :returns: Name of the default Settings
    '''
    return defaultNames[-1]

def popDefaultName():
    '''Removes the last default name and returns it.

    If there is only one name left, it won't be removed.

    :returns: Last default name
    '''
    global defaultNames
    if len(defaultNames) > 1:
        return defaultNames.pop()
    else:
        return defaultNames[0]

def getSettings(name):
    '''Returns the Settings object with the given name.

    :returns: The Settings object with the given name
    '''
    if name in collection:
        return collection[name]

def setSettings(settings):
    '''Adds the given Settings object to the collection.

    A Settings object with the same name will be overridden!

    :param settings: A Settings object
    '''
    global collection
    collection[settings.name] = settings

def setRootSettings(settings):
    '''Sets the root settings

    :param settings: A settings object
    '''
    global collection
    collection[getDefaultName()] = settings

def delSettings(name):
    '''Deletes the settings with the given name

    :param name: Name of the Settings to delete.
    '''
    global collection
    if name in collection:
        del collection[name]

def cloneSettings(source, targetName):
    '''Clones everything except for the clients from the Settings source to the Settings with the name targetName.

    Clones all properties (not the clients) from the Settings source to the Settings with the name targetName and returns the latter.
    If the target can't be found, it will be created but not registered to the SettingsManager.
    Existing properties and the corresponding clients will be overridden!

    :param source: The Settings from which the properties shall be cloned
    :param targetName: The name of the Settings the properties shall be cloned
                       to
    :returns: The Settings with the name targetName
    '''
    sourceSettings = source

    targetSettings = getSettings(targetName)
    if targetSettings is None:
        targetSettings = Settings(targetName)
    if sourceSettings is None:
        return targetSettings
    for n, p in sourceSettings._properties.items():
        targetSettings.registerProperty(n, p.value)
    return targetSettings

def getNextClientName():
    '''Returns the name for the next client.

    Returns a name for a new client. E.g. 'client_001' for the first client.
    Increments the internal counter lastClientId.

    :returns: name for the next client
    '''
    global lastClientId
    lastClientId += 1
    return 'client_%03d' % lastClientId
