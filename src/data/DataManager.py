import numpy as np
import numbers

from data.Data import Data
from data.DataAlias import DataAlias
from data.DataEntry import DataEntry
from data.DataStructure import DataStructure


class DataManager():
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

    def __init__(self, name):
        '''
        Constructor
        :param string name: The name of this DataManager
        '''
        self.name = name
        self.__subDataManager = None
        self.dataEntries = dict()
        self.dataAliases = dict()
        self._dirty = True
        self._finalized = False
        self._depthMap = {}
        self._subDataManagerList = []

    @property
    def finalized(self):
        '''
        Returns True if the DataManager has been finalized,
        False otherwise.
        '''
        return self._finalized

    @property
    def subDataManager(self):
        '''Getter for the subDataManager'''
        return self.__subDataManager

    @subDataManager.setter
    def subDataManager(self, subDataManager):
        '''Sets the subDataManager for this DataManager'''
        self.__subDataManager = subDataManager

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

    def addDataEntry(self, name, numDimensions, minRange=-1, maxRange=1):
        '''
        Function for adding a new data entry. If the same data entry already
        exists, then the properties are overwritten.
        minRange and maxRange are optional arguments (standard values are a
        vector of -1 and +1). Both arguments need to be row vectors with the
        same size as the specified dimensionality.

        :param string name: The name of the data entry
        :param int numDimensions: The number of dimensions of the data entry
        :param minRange: Minimum values (optional)
        :param maxRange: Maximum values (optional)
        :type minRange: list or number
        :type maxRange: list or number
        :raises ValueError: If the DataManager has been finalized already or
                            there is a DataAlias of that name.
        '''
        if self.finalized:
            raise RuntimeError("The data manager cannot be modified after "
                               "it has been finalized")

        # Ensure that the name of the DataEntry does not conflict with an
        # alias name
        if name in self.dataAliases:
            raise ValueError("The name of an alias conflicts with a data " +
                             "entry name: " + name)

        if isinstance(minRange, numbers.Number):
            minRange = minRange * np.ones((numDimensions))

        if isinstance(maxRange, numbers.Number):
            maxRange = maxRange * np.ones((numDimensions))

        self.dataEntries[name] = DataEntry(name, numDimensions,
                                           minRange, maxRange)
        self.dataAliases[name] = DataAlias(name, [(name, ...)], numDimensions)

        self._dirty = True

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

    def addDataAlias(self, aliasName, entryList):
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

        # Ensure that the name of the alias does not conflict with an
        # DataEntry name
        if aliasName in self.dataEntries:
            raise ValueError("The name of an alias conflicts with a data " +
                             "entry name: " + aliasName)

        # Ensure that all referenced names are in the entry list
        if all((entry[0] in self.dataAliases or
                entry[0] in self.dataEntries) for entry in entryList):

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
                                                        0)

            # Computes the total number of dimensions for the alias
            numDim = 0
            for entryName, _slice in self.dataAliases[aliasName].entryList:
                if entryName in self.dataEntries:
                    tmpArray = np.empty((self.dataEntries[entryName]
                                         .numDimensions))
                    numDim += len(tmpArray[_slice])
                else:
                    numDim += self.dataAliases[entryName].numDimensions
            self.dataAliases[aliasName].numDimensions = numDim
        else:
            if self.subDataManager is not None:
                self.subDataManager.addDataAlias(aliasName, entryList)
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
                return self.dataAliases[name].numDimensions
            elif self.subDataManager is not None:
                return self.subDataManager.getNumDimensions(name)
            else:
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

    def getElementNames(self):
        '''
        Returns the names of all data entries (including subdatamanagers)

        :return: The entry names
        :rtype: list of strings
        '''
        names = []
        for name in self.dataEntries.keys():
            names.append(name)
        if (self.subDataManager is not None):
            names.extend(self.subDataManager.getElementNames())
        return names

    def getAliasNamesLocal(self):
        '''
        Returns the names of all aliases (only of this data manager)

        :return: The alias names
        :rtype: list of strings
        '''
        return self.dataAliases.keys()

    def getElementNamesLocal(self):
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
        After finalization, the structure of the data cannot be modified.
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

        dataStructure = DataStructure(numElementsCurrentLayer)
        for dataEntryName, dataEntry in self.dataEntries.items():
            dataStructure.createEntry(dataEntryName,
                                      np.zeros((numElementsCurrentLayer,
                                                dataEntry.numDimensions),
                                               dtype=np.float64))

        for dataAliasName, dataAlias in self.dataAliases.items():
            if dataAliasName not in self.dataEntries:
                dataStructure.createEntry(dataAliasName, dataAlias)

        if (self.subDataManager is not None):
            subDataStructures = []

            for _ in range(0, numElementsCurrentLayer):
                subDS = self.subDataManager._createDataStructure(numElements)
                subDataStructures.append(subDS)

            dataStructure.createEntry(self.subDataManager.name,
                                      subDataStructures)

        return dataStructure

    def reserveStorage(self, dataStructure, numElements):
        '''
        Reserves more storage for a data structure. numElements can be a vector
        that also contains the number of data points to add to the lower levels
        of the hierarchy. This function should only be called by the data
        object.

        :param data.DataStructure dataStructure: The DataStructure to be
                                                 modified
        :param numElements: A vector containing the number of elements to add
                            for each layer
        :type numElemenst: list of ints
        '''
        numElementsLocal = numElements
        if isinstance(numElements, list):
            numElementsLocal = numElements[0]
            numElements = numElements[1:]

        for name, entry in self.dataEntries.items():
            currentSize = dataStructure.dataStructureLocalLayer[
                name].shape[0]
            if currentSize < numElementsLocal:
                dataStructure.dataStructureLocalLayer[name] = np.vstack(
                    (dataStructure.dataStructureLocalLayer[name],
                     np.zeros((numElementsLocal - currentSize,
                               entry.numDimensions))))
            else:
                dataStructure.dataStructureLocalLayer[name] = np.delete(
                    dataStructure.dataStructureLocalLayer[name],
                    slice(numElementsLocal, None, None), 0)

        if self.subDataManager is not None and numElements:
            for subStructure in dataStructure. \
                    dataStructureLocalLayer[self.subDataManager.name]:
                self.subDataManager.reserveStorage(subStructure, numElements)
