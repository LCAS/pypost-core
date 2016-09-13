import numpy as np
import numbers

from pypost.data.Data import Data
from pypost.data.DataAlias import DataAlias, IndexModifier
from pypost.data.DataEntry import DataEntry, DataType
from pypost.common import SettingsManager
from pypost.common.SettingsClient import SettingsClient
from pypost.data.DataStructure import DataStructure

class DataManager(SettingsClient):

    '''
    The data manager stores all properties of the data that we mantain for
    the different experiments. It is organized hierarchically for storing
    data on different time scales. For each level of the hierarchy, we have an
    individual data manager, which need to be connected by setting a
    "subDataManager".

    Data Entries

    Data entries represent the stored data in the DataManager. For example,
    we can store data on the level of the "episodes", e.g., "parameters", or
    on the level of the single steps of an episode, e.g., "states" and
    "actions". For each data entry, we have to set the dimensionality. We also
    can set the range of the data entry.

    Data Aliases

    In addition to data entries, we can define data alias (see addDataAlias).
    A data alias can be seen as a pointer that points to other data entries. It
    can point to a subIndex set of a single data entry or of mulitple data
    entries. For example, we could have the data entries "weights", "goal" and
    "goalVel" (describing the parameters of a DMP). In order to learn all
    parameters at once, we can define a data alias "parameters" that points to
    the concantenation of "weights", "goal" and "goalVel".

    Additional functionality

    The data manager also has the basic functionality you need to obtain
    the properties of the data or to compute the level of the hierarchy
    of a specific data entry. When registering a new data entry, always
    be aware that we have to register it at the correct data manager for
    the desired hierarchy.

    A detailled introduction into the functionality of the DataManager can
    be found in the tutorials directory.
    '''

    def __init__(self, name, isTimeSeries = False):
        '''
        Constructor
        :param string name: The name of this DataManager
        '''
        SettingsClient.__init__(self)

        self.name = name
        self.subDataManager = None
        self.dataEntries = dict()
        self.dataAliases = dict()
        self._dirty = True
        self._finalized = False
        self._depthMap = {}
        self._subDataManagerList = []
        self.isTimeSeries = isTimeSeries

        self.dataPreprocessorsForward = {}
        self.dataPreprocessorsInverse = {}

        def makePeriodic(data, dataItem, index):
            isPeriodic = np.array(self.getPeriodicity(dataItem.name), dtype=bool)
            data[:, isPeriodic] = data[:, isPeriodic] % (2 * np.pi)
            return data

        def restrictData(data, dataItem, index):
            minRange = self.getMinRange(dataItem.name)
            maxRange = self.getMaxRange(dataItem.name)

            data = np.clip(data, minRange, maxRange)
            return data

        def setDataValidTag(data, dataItem, index):
            dataItem.isValid[index] = data
            return dataItem.data[index]

        def getDataValidTag(data, dataItem, index):
            return dataItem.isValid[index]

        self.addDataPreprocessor('periodic', makePeriodic)
        self.addDataPreprocessor('restricted', restrictData)
        self.addDataPreprocessor('validFlag', getDataValidTag, setDataValidTag)

    @property
    def finalized(self):
        '''
        Returns True if the DataManager has been finalized,
        False otherwise.
        '''
        return self._finalized


    def getSubDataManagerForDepth(self, depth):
        '''
        Returns the DataManager for the given depth.
        Returns None if depth is out of range.

        :return: The DataManager associated with the given depth
        :rtype: data.DataManager
        '''
        if self._dirty:
            self.updateDepthMap(False)

        if depth >= 0 and depth < len(self._subDataManagerList):
            return self._subDataManagerList[depth]
        return None

    def getDepthForDataManager(self, dataManagerName):
        if (self.name == dataManagerName):
            return 0
        else:
            if (not self.subDataManager):
                raise ValueError('Datamanager for {0} not found'.format(dataManagerName))
            else:
                return self.subDataManager.getDepthForDataManager(dataManagerName) + 1

    def addOptionalDataEntry(self, name, defaultGuard, numDimensions, minRange = None, maxRange = None, parameterPoolName = None, level = 0, transformation = None):

        if minRange is None:
            minRange = -np.ones(numDimensions)

        if maxRange is None:
            maxRange = np.ones(numDimensions)

        nameUpper = name[0].upper() + name[1:]
        guard = 'use' + nameUpper

        self.settings.registerProperty(guard, defaultGuard)
        self.settings.registerProperty(name, (minRange + maxRange) / 2)
        self.settings.registerProperty('min' + nameUpper, minRange)
        self.settings.registerProperty('max' + nameUpper, maxRange)

        if self.settings.getProperty(guard):

            dataManagerForDepth = self.getSubDataManagerForDepth(level)
            dataManagerForDepth.addDataEntry(name, numDimensions, minRange, maxRange)

            if parameterPoolName is not None:

                if transformation is None:
                    dataManagerForDepth.addDataAlias(parameterPoolName, [(name, ...)])

                elif transformation == 'logsig':

                    nameData = name + 'Sigmoid'
                    dataManagerForDepth.addDataAlias(parameterPoolName, [(nameData, ...)])
        else:
            dataManagerForDepth = self.getSubDataManagerForDepth(level)
            dataManagerForDepth.addDataEntry(name, numDimensions, minRange, maxRange, takeFromSettings=True)

        self._dirty = True
        self.settings.lockProperty(guard)


    def addDataEntry(self, name, numDimensions, minRange=-1, maxRange=1, isPeriodic = None, dataType = DataType.continuous, takeFromSettings = False):
        '''
        Function for adding a new data entry. If the same data entry already
        exists, then the properties are overwritten.
        minRange and maxRange are optional arguments (standard values are a
        vector of -1 and +1). Both arguments need to be row vectors with the
        same size as the specified dimensionality.

        :param string name: The name of the data entry
        :param int numDimensions: The number of dimensions of the data entry
        :param minRange: Minimum values (optional, defaults to -1)
        :param maxRange: Maximum values (optional, defaults to +1)
        :type minRange: list or number
        :type maxRange: list or number
        :raises ValueError: If the DataManager has been finalized already or
                            there is a DataAlias of that name.
        '''

        settings = SettingsManager.getDefaultSettings()

        name = name + settings.getSuffixString()

        if self.finalized:
            raise RuntimeError("The data manager cannot be modified after "
                               "it has been finalized")

        # Ensure that the name of the data entry does not conflict with an
        # alias name
        if name in self.dataAliases:
            raise ValueError("The name of an alias conflicts with a data " +
                             "entry name: " + name)

        if not isinstance(numDimensions, tuple):
            numDimensions = (numDimensions,)

        if isinstance(minRange, numbers.Number):
            minRange = minRange * np.ones(numDimensions)

        if isinstance(maxRange, numbers.Number):
            maxRange = maxRange * np.ones(numDimensions)

        self.dataEntries[name] = DataEntry(name, numDimensions,
                                           minRange, maxRange, isPeriodic, dataType, takeFromSettings)
        self.dataAliases[name] = DataAlias(name, [(name, ...)], numDimensions)
        self._dirty = True

        if (self.isTimeSeries):
            # add Aliases for time series
            nameUpper = name[0].upper() + name[1:]
            aliasName = 'next' + nameUpper
            self.dataAliases[aliasName] = DataAlias(aliasName, [(name, ...)], numDimensions, IndexModifier.next)

            aliasName = 'last' + nameUpper
            self.dataAliases[aliasName] = DataAlias(aliasName, [(name, ...)], numDimensions, IndexModifier.last)

            aliasName = 'all' + nameUpper
            self.dataAliases[aliasName] = DataAlias(aliasName, [(name, ...)], numDimensions, IndexModifier.all)

    def addFeatureMapping(self, mapping):
        outputVariable = mapping.getOutputVariables()[0]
        if (not outputVariable in self.dataEntries):
            raise ValueError('Can only add Feature Mapping for existing data entries. Current Entry %s does not exist' % outputVariable)

        self.dataEntries[outputVariable].isFeature = True
        self.dataEntries[outputVariable].callBackGetter = mapping



    def isDataEntry(self, entryName):
        '''
        Checks if an entry with the given name exists

        :param entryName: the entry name to query
        '''
        if entryName in self.dataEntries:
            return True

        if self.subDataManager is not None:
            return self.subDataManager.isDataEntry(entryName)

        return False

    def setRange(self, entryName, minRange, maxRange):
        '''Sets the min and max range for existing data entries

        :param entryName: The name of the exisiting data entry
        :type entryName: string
        :param minRange: the new min range for the data entry
        :type minRange: np.ndarray
        :param maxRange: the new max range for the data entry
        :type maxRange: np.ndarray
        '''
        if self.finalized:
            raise RuntimeError("The data manager cannot be modified after "
                               "it has been finalized")

        if entryName in self.dataEntries:
            entry = self.dataEntries[entryName]

            if (minRange.shape != entry.minRange.shape):
                raise ValueError("The shape of the specified minRange (%s)"
                                 " doesn't match the existing range (%s)"
                                 % (minRange.shape, entry.minRange.shape))

            if (maxRange.shape != entry.maxRange.shape):
                raise ValueError("The shape of the specified maxRange (%s)"
                                 " doesn't match the existing range (%s)"
                                 % (maxRange.shape, entry.maxRange.shape))

            entry.minRange = minRange
            entry.maxRange = maxRange
            return

        if self.subDataManager is not None:
            return self.subDataManager.setRange(entryName, minRange, maxRange)

        raise ValueError("Entry %s is not registered!" % entryName)

    def _checkForAliasCycle(self, aliasName, entryList):
        '''
        Detects circular dependencies between aliases.
        It is assumed that the entryList is valid, i.e. all entry names
        correspond either to valid entries or aliases.

        :param string aliasName: The name of the alias to check
        :param list entryList: The entryList of the alias to check
        '''
        for entry in entryList:
            if entry[0] not in self.dataEntries:
                if aliasName == entry[0]:
                    return True
                return self._checkForAliasCycle(aliasName,
                                                self.dataAliases[entry[0]]
                                                .entryList)
        return False

    def getDataPreprocessorForward(self, processorName):
        if not processorName in self.dataPreprocessorsForward:
            raise ValueError('Unknown data-preprocessor %s!' % processorName)
        return self.dataPreprocessorsForward[processorName]

    def getDataPreprocessorInverse(self, processorName):
        if not processorName in self.dataPreprocessorsInverse:
            raise ValueError('Unknown data-preprocessor %s!' % processorName)
        return self.dataPreprocessorsInverse[processorName]

    def addDataPreprocessor(self, processorName, dataPreprocessorForward, dataPreprocessorInverse = lambda x: x):
        self.dataPreprocessorsForward[processorName] = dataPreprocessorForward
        self.dataPreprocessorsInverse[processorName] = dataPreprocessorInverse

    def imposeSuffix(self, argumentList, suffix):
        for i in range(0, len(argumentList)):
            name = argumentList[i][0]
            if len(name) > 8 and name[-8:] == 'NoSuffix':
                name = name[0:-8]
            else:
                nameWithSuffix = name + suffix
                if self.isDataEntry(nameWithSuffix):
                    name = nameWithSuffix

            argumentList[i] = (name,argumentList[i][1])
        return argumentList

    def addDataAlias(self, aliasName, entryList, indexModifier = IndexModifier.none):
        '''
        Adds a new data alias.


        :param string aliasName: The name of the alias
        :param entryList: A list containing tuples of data entries and slices.
                         If the whole data entry should be used, use
                         "..." instead of a slice. This means the alias should
                         point to all dimensions of the data entry.
                         See :mod:`~data.DataAlias` for more information about
                         the format of this parameter
        :type entryList: list of tuples
        :raises RuntimeError: If the DataManager has been finalized already.
        :raises ValueError: If the alias name is already used as data entry
                            or an entry in the entryList doesn't exist.
        '''

        if self.finalized:
            raise RuntimeError("The data manager cannot be modified after " +
                               "it has been finalized")

        if not isinstance(entryList, list):
            entryList = [entryList]

        settings = self.settings
        aliasName = aliasName + settings.getSuffixString()
        entryList = self.imposeSuffix(entryList, settings.getSuffixString())


        # Ensure that the name of the alias does not conflict with an
        # DataEntry name
        if aliasName in self.dataEntries:
            raise ValueError("The name of an alias conflicts with a data " +
                             "entry name: " + aliasName)

        # Ensure that all referenced names are in the entry list
        if all((entry[0] in self.dataAliases or
                entry[0] in self.dataEntries ) for entry in entryList):

            if self._checkForAliasCycle(aliasName, entryList):
                raise ValueError("Alias cycle detected!")

            # Test if the alias has already been defined
            if aliasName in self.dataAliases:
                # the alias exists. Check all entries of the new alias
                for entry in entryList:
                    i = 0
                    entryFound = False
                    for aliasEntryName, _ in \
                            self.dataAliases[aliasName].entryList:
                        if entry[0] == aliasEntryName:
                            # replace existing entry
                            self.dataAliases[aliasName].entryList[i] = entry
                            entryFound = True
                            break
                        i += 1

                    if not entryFound:
                        # add new entry to existing entries
                        self.dataAliases[aliasName].entryList.append(entry)
            else:
                # add the entryList
                self.dataAliases[aliasName] = DataAlias(aliasName, entryList,
                                                        0, indexModifier)



            # Computes the total number of dimensions for the alias
            numDim = 0
            for entryName, _slice in self.dataAliases[aliasName].entryList:
                if entryName in self.dataEntries:
                    numDimLocal = self.dataEntries[entryName].numDimensions
                    if len(numDimLocal) > 1:
                        raise ValueError("Only vector-valued data entries can be stacked in aliases")
                    else:
                        numDimLocal = numDimLocal[0]
                    tmpArray = np.empty((numDimLocal))

                    numDim += len(tmpArray[_slice])
                else:
                    numDim += self.dataAliases[entryName].numDimensions[0]


            self.dataAliases[aliasName].numDimensions = (numDim,)

            if (self.isTimeSeries):
                # add Aliases for time series
                nameUpper = aliasName[0].upper() + aliasName[1:]
                aliasAliasName = 'next' + nameUpper
                self.dataAliases[aliasAliasName] = DataAlias(aliasAliasName, [(aliasName, ...)], numDim,
                                                        IndexModifier.next)

                aliasAliasName = 'last' + nameUpper
                self.dataAliases[aliasAliasName] = DataAlias(aliasAliasName, [(aliasName, ...)], numDim,
                                                        IndexModifier.last)

                aliasAliasName = 'all' + nameUpper
                self.dataAliases[aliasAliasName] = DataAlias(aliasAliasName, [(aliasName, ...)], numDim, IndexModifier.all)
        else:
            if self.subDataManager is not None:
                self.subDataManager.addDataAlias(aliasName, entryList, indexModifier)
            else:
                raise ValueError("One or more of the alias entry names do " +
                                 "not exist")
        self._dirty = True

    def getDataAlias(self, aliasName):
        '''
        Retuns the data alias associated with the given name.

        :param string aliasName: The alias name
        :return: The data alias
        :rtype: data.DataAlias
        :raises ValueError: If the alias is not defined
        '''
        if aliasName in self.dataAliases:
            return self.dataAliases[aliasName]
        if self.subDataManager is not None:
            return self.subDataManager.getDataAlias(aliasName)
        raise ValueError("Alias of name %s is not defined" % aliasName)

    def getDataEntry(self, entryName):
        '''
        Retuns the data alias associated with the given name.

        :param string entryName: The alias name
        :return: The data alias
        :rtype: data.DataAlias
        :raises ValueError: If the alias is not defined
        '''
        if entryName in self.dataEntries:
            return self.dataEntries[entryName]
        if self.subDataManager is not None:
            return self.subDataManager.getDataEntry(entryName)
        raise ValueError("Alias of name %s is not defined" % entryName)

    def getDataEntryDepth(self, entryName):
        '''
        Returns the depth of the given entry.

        :param string entryName: The entry name
        :return: The depth of the entry
        :rtype: int
        '''
        if self._dirty:
            self.updateDepthMap(False)
        if entryName not in self._depthMap:
            raise ValueError("Entry %s is not registered!" % entryName)
        return self._depthMap[entryName]

    def getNumDimensions(self, entryNames):
        '''
        Returns the dimensionality of a given data entry (or alias).
        If multiple names are given, the dimensions are added up.
        Also works if the name has been registered on a deeper layer.

        :param entryNames: The name(s) of the entries or aliases
        :type entryNames: string or list of strings
        :return: The number of dimensions
        :rtype: int
        :raises ValueError: If an entry/alias is not defined
        '''
        if isinstance(entryNames, list):
            numDim = 0
            for name in entryNames:
                numDim += self.getNumDimensions(name)
            return numDim
        else:
            name = entryNames
            if name in self.dataAliases:
                if (len(self.dataAliases[name].numDimensions) == 1):
                    return self.dataAliases[name].numDimensions[0]
                else:
                    return self.dataAliases[name].numDimensions
            elif self.subDataManager is not None:
                return self.subDataManager.getNumDimensions(name)
            else:
                raise ValueError("Entry %s is not registered!" % name)

    def getPeriodicity(self, entryNames):
        if isinstance(entryNames, list):
            periodicity = []
            for name in entryNames:
                periodicity = periodicity + self.getPeriodicity(name)
            return periodicity

        name = entryNames
        if name in self.dataAliases:
            alias = self.dataAliases[name]
            periodicity = [False] * alias.numDimensions[0]
            index = 0
            for entryName, _slice in alias.entryList:
                tempMinRange = None
                if entryName in self.dataEntries:
                    if (_slice == Ellipsis):
                        tempPeriodicity = self.dataEntries[entryName].isPeriodic
                    else:
                        tempPeriodicity = self.dataEntries[entryName].isPeriodic[_slice]
                elif entryName in self.dataAliases:
                    tempPeriodicity = self.getPeriodicity(entryName)
                else:
                    raise ValueError("Unknown entry.")

                periodicity[index:(index + len(tempPeriodicity))] = tempPeriodicity
                index += len(tempPeriodicity)
            return periodicity

        if self.subDataManager is not None:
            return self.subDataManager.getPeriodicity(name)

        raise ValueError("Entry %s is not registered!" % name)

    def getMinRange(self, entryNames):
        '''
        Returns a vector with the minRange values for each entry.
        Also works for a single entry name.

        :param entryNames: The entry/alias names
        :type entryNames: string or list of strings
        :return: A list containing the minRange values
        :rtype: list of numbers
        :raises ValueError: If an entry or alias is not defined
        '''
        if isinstance(entryNames, list):
            minRange = []
            for name in entryNames:
                minRange = np.hstack((minRange, self.getMinRange(name)))
            return minRange

        name = entryNames
        if name in self.dataAliases:
            alias = self.dataAliases[name]
            minRange = np.zeros((alias.numDimensions))
            index = 0
            for entryName, _slice in alias.entryList:
                tempMinRange = None
                if entryName in self.dataEntries:
                    tempMinRange = self.dataEntries[entryName].minRange[_slice]
                elif entryName in self.dataAliases:
                    tempMinRange = self.getMinRange(entryName)
                else:
                    raise ValueError("Unknown entry.")

                minRange[index:(index + len(tempMinRange))] = tempMinRange

                index += len(tempMinRange)
            return minRange

        if self.subDataManager is not None:
            return self.subDataManager.getMinRange(name)

        raise ValueError("Entry %s is not registered!" % name)

    def getMaxRange(self, entryNames):
        '''
        Returns a vector with the maxRange values for each entry.
        Also works for a single entry name.

        :param entryNames: The entry/alias names
        :type entryNames: string or list of strings
        :return: A list containing the maxRange values
        :rtype: list of numbers
        :raises ValueError: If an entry or alias is not defined
        '''
        if isinstance(entryNames, list):
            maxRange = []
            for name in entryNames:
                maxRange = np.hstack((maxRange, self.getMaxRange(name)))
            return maxRange
        name = entryNames

        if name in self.dataAliases:
            alias = self.dataAliases[name]
            maxRange = np.zeros((alias.numDimensions))
            index = 0
            for entryName, _slice in alias.entryList:
                tempMaxRange = None
                if entryName in self.dataEntries:
                    tempMaxRange = self.dataEntries[entryName].maxRange[_slice]
                elif entryName in self.dataAliases:
                    tempMaxRange = self.getMaxRange(entryName)
                else:
                    raise ValueError("Unknown entry.")

                maxRange[index:(index + len(tempMaxRange))] = tempMaxRange
                index += len(tempMaxRange)
            return maxRange

        if self.subDataManager is not None:
            return self.subDataManager.getMaxRange(name)

        raise ValueError("Entry %s is not registered!" % name)

    def getAliasNames(self):
        '''
        Returns the names of all aliases (including subdatamanagers)

        :return: The alias names
        :rtype: list of strings
        '''
        names = []
        for name in self.dataAliases.keys():
            names.append(name)
        if (self.subDataManager is not None):
            names.extend(self.subDataManager.getAliasNames())
        return names


    def getEntryNames(self):
        '''
        Returns the names of all data entries (including subdatamanagers)

        :return: The entry names
        :rtype: list of strings
        '''
        names = []
        for name in self.dataEntries.keys():
            names.append(name)
        if (self.subDataManager is not None):
            names.extend(self.subDataManager.getEntryNames())
        return names

    def getAliasNamesLocal(self):
        '''
        Returns the names of all aliases (only of this data manager)

        :return: The alias names
        :rtype: list of strings
        '''
        return self.dataAliases.keys()

    def getEntryNamesLocal(self):
        '''
        Returns the names of all data entries (only of this data manager)

        :return: The entry names
        :rtype: list of strings
        '''
        return self.dataEntries.keys()

    def getDataObject(self, numElements):
        '''
        Creates a new data object with numElements data points.

        :param numElements: A vector defining the number of elements for each
                           layer of the hierarchy.
                           This parameter may also be an integer, in which case
                           all layers will have the same number of data points
        :type numElements: int or list of ints
        :return: The newly created data object
        :rtype: data.Data
        '''
        if not self.finalized:
            self.finalize()
        return Data(self, self._createDataStructure(numElements))

    def finalize(self):
        '''
        Finalizes this data manager.
        After finalization, the structure of the data cannot be modified any
        more.
        '''
        self.updateDepthMap(True)

    def updateDepthMap(self, finalize):
        '''
        Updates the internal depth map used for fast data access.
        This function is called automatically during finalization.

        :param bool finalize: If true, the data manager is marked as finalized
        '''
        if self._dirty:
            subManager = self
            depth = 0

            self._subDataManagerList.append(self)

            while subManager is not None:
                entryNames = subManager.getAliasNamesLocal()
                for entryName in entryNames:
                    self._depthMap[entryName] = depth

                if depth > 0:
                    subManager.updateDepthMap(finalize)
                    self._subDataManagerList.append(subManager)

                depth += 1
                subManager = subManager.subDataManager

        self._dirty = False

        if finalize:
            self._finalized = True

    def printDataAliases(self):

        object = self.getDataObject(0)
        object.printDataAliases()

    def _createDataStructure(self, numElements):
        '''
        Creates the data structure (containing real data) for the data object.

        :param numElements: A vector defining the number of elements for each
                           layer of the hierarchy.
                           This parameter may also be an integer, in which case
                           all layers will have the same number of data points.
        :return: The newly created data structure
        :rtype: data.DataStructure
        '''
        if isinstance(numElements, list):
            numElementsCurrentLayer = numElements[0]
            numElements = numElements[1:]
        else:
            numElementsCurrentLayer = numElements


        dataStructure = DataStructure(self, numElementsCurrentLayer, self.isTimeSeries)
        for dataEntryName, dataEntry in self.dataEntries.items():
            dataStructure.createEntry(dataEntryName, dataEntry)

        for dataAliasName, dataAlias in self.dataAliases.items():
            if dataAliasName not in self.dataEntries:
                dataStructure.createAlias(dataAliasName, dataAlias)

        if (self.subDataManager is not None):
            subDataStructures = []

            for _ in range(0, numElementsCurrentLayer):
                subDS = self.subDataManager._createDataStructure(numElements)
                subDataStructures.append(subDS)

            dataStructure.createAliasSubDataStructure(self.subDataManager.name,
                                      subDataStructures)

        return dataStructure



    def mergeDataStructures(self, dataStructure1, dataStructure2):
        '''
        Merges two data structures together.
        The entries of the first data structure will be in front.
        :param dataStructure1: The first data structure
        :param dataStructure2: The second data structure
        :return: The result of the merge operation
        '''
        for entry in self.dataEntries:
            dataStructure1.dataStructureLocalLayer[entry].data = \
                np.vstack((dataStructure1[entry], dataStructure2[entry]))
        dataStructure1.numElements = dataStructure1.numElements + \
            dataStructure2.numElements

        if self.subDataManager is not None:
            subName = self.subDataManager.name
            dataStructure1.dataStructureLocalLayer[subName] = \
                dataStructure1[subName] + dataStructure2[subName]
        return dataStructure1

    def getDataManagerForName(self, managerName):
            '''Returns the data manager with a specific name; e.g. episodes.
            '''
            if managerName == self.name:
                return self
            elif self.subDataManager is None:
                return None
            else:
                return self.subDataManager.getDataManagerForName(managerName)
