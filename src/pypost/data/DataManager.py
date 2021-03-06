import numpy as np
import numbers
import tensorflow as tf

from pypost.data.Data import Data
from pypost.data.DataAlias import DataAlias
from pypost.data.DataAlias import IndexModifierBase
from pypost.data.DataAlias import IndexModifierAll
from pypost.data.DataAlias import IndexModifierNext
from pypost.data.DataAlias import IndexModifierLast
from pypost.data.DataAlias import IndexModifierTimeWindow

from pypost.data.DataEntry import DataEntry, DataType
from pypost.common import SettingsManager
from pypost.common.SettingsClient import SettingsClient
from pypost.data.DataStructure import DataStructure
import pypost.common.tfutils as tfutils


def createDataManagers(names, isTimeSeries):
    if not isinstance(names, list):
        if (isTimeSeries):
            dataManager = DataManagerTimeSeries(names)
        else:
            dataManager = DataManager(names)
    else:

        if (isTimeSeries[0]):
            dataManager = DataManagerTimeSeries(names[0])
        else:
            dataManager = DataManager(names[0])

        currentManager = dataManager
        for i in range(1, len(names)):
            if (isTimeSeries[i]):
                currentManager.subDataManager = DataManagerTimeSeries(names[i])
            else:
                currentManager.subDataManager = DataManager(names[i])

            currentManager = currentManager.subDataManager

    return dataManager


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

    def __init__(self, name):
        '''
        Constructor
        :param string name: The name of this DataManager
        '''
        SettingsClient.__init__(self)

        if isinstance(name, list):
            self.name = name[0]
            nameManagers = name[1:]
        else:
            self.name = name

        self.subDataManager = None
        self.dataEntries = dict()
        self.dataAliases = dict()
        self._dirty = True
        self._finalized = False
        self._depthMap = {}
        self._subDataManagerList = []

        self.dataPreprocessorsForward = {}
        self.dataPreprocessorsInverse = {}

        self.tensorDict = {}
        self.tensorToEntryMap = {}

        self.addDataPreprocessor('periodic', makePeriodic)
        self.addDataPreprocessor('restricted', restrictData)
        self.addDataPreprocessor('validFlag', getDataValidTag, setDataValidTag)

        self.addDataEntry('empty', 0)



    def __getnewargs__(self):
        return (self.name,)

    def __getstate__(self):
        import copy
        subManagerState = None
        if (self.subDataManager):
            subManagerState = self.subDataManager.__getstate__()

        dictState = {}
        dictState['name'] = self.name
        dictState['subDataManager'] = self.subDataManager
        dataEntriesNoFeatures = {}
        for key in self.dataEntries:
            dataEntry = copy.copy(self.dataEntries[key])
            dataEntry.isFeature = False
            dataEntry.callBackGetter = None
            dataEntriesNoFeatures[key] = dataEntry

        dictState['dataEntries'] = dataEntriesNoFeatures
        dictState['dataAliases'] = self.dataAliases

        dictState['_dirty'] = self._dirty
        dictState['_finalized'] = self._finalized
        dictState['_depthMap'] = self._depthMap
        dictState['_subDataManagerList'] = self._subDataManagerList

        return dictState

    def __setstate__(self, state):

        self.name = state['name']

        self.subDataManager = None
        if (state['subDataManager'] is not None):
            self.subDataManager = state['subDataManager']

        self.dataEntries = state['dataEntries']
        self.dataAliases = state['dataAliases']
        self._dirty = True
        self._finalized = False
        self._depthMap = state['_depthMap']
        self._subDataManagerList = state['_subDataManagerList']

        self.dataPreprocessorsForward = {}
        self.dataPreprocessorsInverse = {}

        self.tensorDict = {}
        self.tensorToEntryMap = {}

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

    def getDataManagerForAlias(self, aliasName):
        aliasNames = self.getAliasNamesLocal()
        if aliasName in aliasNames:
            return self
        else:
            if self.subDataManager:
                return self.subDataManager.getDataManagerForAlias(aliasName)
            else:
                return None


    def getDataManagerForLevel(self, depth):
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

    def getLevelForDataManager(self, dataManagerName):
        if (self.name == dataManagerName):
            return 0
        else:
            if (not self.subDataManager):
                raise ValueError('Datamanager for {0} not found'.format(dataManagerName))
            else:
                return self.subDataManager.getLevelForDataManager(dataManagerName) + 1

    def getMaxDepth(self):
        if (self.subDataManager):
            return self.subDataManager.getMaxDepth() + 1
        else:
            return 0

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

            dataManagerForDepth = self.getDataManagerForLevel(level)
            dataManagerForDepth.addDataEntry(name, numDimensions, minRange, maxRange)

            if parameterPoolName is not None:

                if transformation is None:
                    dataManagerForDepth.addDataAlias(parameterPoolName, [(name, ...)])

                elif transformation == 'logsig':

                    nameData = name + 'Sigmoid'
                    dataManagerForDepth.addDataAlias(parameterPoolName, [(nameData, ...)])
        else:
            dataManagerForDepth = self.getDataManagerForLevel(level)
            dataManagerForDepth.addDataEntry(name, numDimensions, minRange, maxRange, takeFromSettings=True)

        self._dirty = True
        self.settings.lockProperty(guard)

        return self.settings.getProperty(guard)


    def addDataEntry(self, name, numDimensions, minRange=-1, maxRange=1, isPeriodic = None, dataType = DataType.continuous, takeFromSettings = False, level = 0):
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

        if (not isinstance(dataType, DataType)):
            raise ValueError('Given dataType needs to be instance of enum Data.DataType!')

        if (level > 0):
            subManager = self.getDataManagerForLevel(level)
            subManager.addDataEntry(name = name, numDimensions=numDimensions, minRange=minRange, maxRange = maxRange, isPeriodic = isPeriodic, dataType=dataType, takeFromSettings=takeFromSettings)
            self._dirty = True
        else:
            settings = SettingsManager.getDefaultSettings()

            name = name + settings.getSuffixString()

            if self.finalized:
                raise RuntimeError("The data manager cannot be modified after "
                                   "it has been finalized (data object has been created). Please apply all modifications"
                                   "to the manager before creating data objects!")

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

            self.addIndexModifiers(name, numDimensions)

    def addIndexModifiers(self, name, numDimensions):
        return

    def addFeatureMapping(self, mapping):

        if isinstance(mapping, tf.Tensor):
            from pypost.mappings import TFMapping
            mapping = TFMapping(self, tensorNode = mapping)

        outputVariable = mapping.getOutputVariables()[0]
        if (not outputVariable in self.dataEntries):
            if (self.subDataManager):
                self.subDataManager.addFeatureMapping(mapping)
            else:
                raise ValueError('Can only add Feature Mapping for existing data entries (aliases are not supported). Current Entry %s does not exist' % outputVariable)

        else:
            self.dataEntries[outputVariable].isFeature = True
            self.dataEntries[outputVariable].callBackGetter = mapping

        self.addDataEntry(outputVariable + '_validFlag', 1)

    def checkDataEntries(self, entryList, errorMessage):

        for i in range(0, len(entryList)):
            if not self.isDataAlias(entryList[i]):
                raise ValueError('Checking entries {}: Entry {} does not exist in data manager'.format(errorMessage, entryList[i]))


    def isDataEntry(self, entryName):
        '''
        Checks if an entry with the given name exists

        :param entryName: the entry name to query
        '''

        if '__' in entryName:
            index = entryName.find('__')
            entryName =  entryName[:index]

        if entryName in self.dataEntries:
            return True

        if self.subDataManager is not None:
            return self.subDataManager.isDataEntry(entryName)

        return False

    def isDataAlias(self, entryName):
        '''
        Checks if an entry with the given name exists

        :param entryName: the entry name to query
        '''

        if '__' in entryName:
            index = entryName.find('__')
            entryName =  entryName[:index]

        if entryName in self.dataAliases:
            return True

        if self.subDataManager is not None:
            return self.subDataManager.isDataAlias(entryName)

        return False

    def getTensorInputOutput(self, tensorNode):
        if isinstance(tensorNode, (list, tuple)):
            placeHolderList = set()
            for tensor in tensorNode:
                if not isinstance(tensor, (tf.Tensor, tf.Variable, tf.Operation)):
                    raise ValueError('TF Mappings can only be created for tf.Tensor objects or list/tuple of those')
                placeHolderList = placeHolderList | tfutils.list_data_placeholders(self, tensor)
        elif isinstance(tensorNode, (tf.Tensor, tf.Variable, tf.Operation)):
            placeHolderList = tfutils.list_data_placeholders(self, tensorNode)
        else:
            raise ValueError('TF Mappings can only be created for tf.Tensor objects or list/tuple of those')
        inputVariables = []
        placeHolderList = list(placeHolderList)
        for placeHolder in placeHolderList:
            inputVariables.append(self.getEntryForTensor(placeHolder))

        if isinstance(tensorNode, (list, tuple)):
            outputVariables = []
            tensorNodes = []
            tensorNodesEntry = []

            for tensor in tensorNode:
                if self.isEntryTensor(tensor):
                    outputVariables.append(self.getEntryForTensor(tensor))
                    tensorNodesEntry.append(tensor)
                else:
                    tensorNodes.append(tensor)

            tensorNode = tensorNodesEntry + tensorNodes

        else:
            if self.isEntryTensor(tensorNode):
                outputVariables = self.getEntryForTensor(tensorNode)
            else:
                outputVariables = []

        return inputVariables, outputVariables, placeHolderList, tensorNode

    def printTensorInputOutput(self, tensorNode):
        inputVariables, outputVariables, *args = self.getTensorInputOutput(tensorNode)
        print('{} -> {}'.format(inputVariables, outputVariables))

    def getEmptyTensor(self):
        return self.emptyTensor


    def createTensorForEntry(self, entryName, suffix = None):

        if suffix:
            dictEntry = entryName + '_' + suffix
        else:
            dictEntry = entryName

        if dictEntry in self.tensorDict:
            return self.tensorDict[dictEntry]
        else:
            dim = self.getNumDimensions(entryName)
            if (isinstance(dim, tuple)):
                tensor = tf.placeholder(tf.float32, shape=(None,) + dim, name = dictEntry)
            else:
                tensor = tf.placeholder(tf.float32, shape=(None, dim), name=dictEntry)

            self.tensorToEntryMap[tensor] = entryName
            self.tensorDict[dictEntry] = tensor
            return tensor

    def isEntryTensor(self, tensor):
        return tensor in self.tensorToEntryMap

    def getEntryForTensor(self, tensor):
        if tensor not in self.tensorToEntryMap:
            raise ValueError('Tensor is not registred as entry tensor!')

        return self.tensorToEntryMap[tensor]

    def connectTensorToEntry(self, tensor, entryName):
        self.tensorToEntryMap[tensor] = entryName

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

    def addDataAlias(self, aliasName, entryList, indexModifier = IndexModifierBase(), useConcatVertical = False, addStandardModifiers = True):
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
                if (useConcatVertical != self.dataAliases[aliasName].useConcatVertical):
                    raise ValueError("Cannot change alignment of data alias (vertical or horizontal)!")
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
                                                        0, indexModifier, useConcatVertical=useConcatVertical)

            # Computes the total number of dimensions for the alias
            numDim = 0
            # check if all entries of alias have same number of dimensions for vertical alignment!
            if self.dataAliases[aliasName].useConcatVertical and len(self.dataAliases[aliasName].entryList) > 0:
                numDim = -1
                for entryName, _slice in self.dataAliases[aliasName].entryList:
                    if entryName in self.dataEntries:
                        numDimLocal = self.dataEntries[entryName].numDimensions
                        if len(numDimLocal) > 1:
                            raise ValueError("Only vector-valued data entries can be stacked in aliases")
                        else:
                            numDimLocal = numDimLocal[0]
                        tmpArray = np.empty((numDimLocal))

                        numDimLocal = len(tmpArray[_slice])
                    else:
                        numDimLocal = self.dataAliases[entryName].numDimensions[0]

                    if (numDim >= 0):
                        if (numDim != numDimLocal):
                            raise ValueError('Can not create data alias with vertical alignment: {} has wrong number of dimensions ! ({} instead of {})'.format(entryName, numDimLocal, numDim))
                    else:
                        numDim = numDimLocal
            else:
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

            numDim = numDim * indexModifier.dimensionMultiplier
            self.dataAliases[aliasName].numDimensions = (numDim,)

            if (addStandardModifiers):
                self.addIndexModifiers(aliasName, numDim)
        else:
            if self.subDataManager is not None:
                self.subDataManager.addDataAlias(aliasName, entryList, indexModifier, useConcatVertical=useConcatVertical)
            else:
                raise ValueError("One or more of the alias entry names do " +
                                 "not exist")
        self._dirty = True

    def getDataAliases(self):
        return self.dataAliases

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

    def getDataEntries(self):
        return self.dataEntries

    def getDataType(self, entryName):

        if self.isDataEntry(entryName):
            entry = self.getDataEntry(entryName)
            return entry.dataType

        elif self.isDataAlias(entryName):
            alias = self.getDataAlias(entryName)

            dataType = self.getDataType(alias.entryList[0])

            for i in range(1, len(alias.entryList)):
                dataType_ = self.getDataType(alias.entryList[i])

                if (dataType_ != dataType):
                    dataType = DataType.continuous

            return dataType
        else:
            raise ValueError('Getting entry type: {} entry is unknown!'.format(entryName))

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

    def getDataEntryLevel(self, entryName):
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
                if (self.dataAliases[name].useConcatVertical):
                    break
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

                if (self.dataAliases[name].useConcatVertical):
                    break

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
                if (self.dataAliases[name].useConcatVertical):
                    break
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

    def createDataObject(self, numElements):
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
        if (not isinstance(numElements, list)):
            numElements = [numElements]

        if len(numElements) < self.getMaxDepth() + 1:
            numElements = numElements + [0]* (self.getMaxDepth() + 1 - len(numElements))

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

        object = self.createDataObject(0)
        object.printDataAliases()

    def isTimeSeries(self):
        return False

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


        dataStructure = DataStructure(self, numElementsCurrentLayer, self.isTimeSeries())
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


class DataManagerTimeSeries(DataManager):

    def __init__(self, name):

        DataManager.__init__(self, name)

        self.addDataEntry('timeSteps', 1, dataType=DataType.index)

    def addIndexModifiers(self, name, numDimensions):
        # add Aliases for time series
        nameUpper = name[0].upper() + name[1:]
        aliasName = 'next' + nameUpper
        self.dataAliases[aliasName] = DataAlias(aliasName, [(name, ...)], numDimensions, IndexModifierNext())

        aliasName = 'last' + nameUpper
        self.dataAliases[aliasName] = DataAlias(aliasName, [(name, ...)], numDimensions, IndexModifierLast())

        aliasName = 'all' + nameUpper
        self.dataAliases[aliasName] = DataAlias(aliasName, [(name, ...)], numDimensions, IndexModifierAll())

    def isTimeSeries(self):
        return True

    def addDataWindowAlias(self, aliasName, entryList, indexTimeBegin, indexTimeEnd, dropBoundarySamples = False):

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

        indexModifier = IndexModifierTimeWindow(indexTimeBegin, indexTimeEnd, dropOutSamples=dropBoundarySamples)
        self.addDataAlias(aliasName, entryList, indexModifier=indexModifier, addStandardModifiers = False)