from pypost.common.Settings import Settings
from pypost.common import SettingsManager
import sys
import os
import random
import traceback
import numpy as np
from enum import Enum
from pypost.common.SettingsClient import SettingsClient
from collections import namedtuple
from pypost.common import DataPrinter
import yaml
import shlex, subprocess

StoringType = Enum('StoringType', 'STORE, STORE_PER_ITERATION, ACCUMULATE, '
                   'ACCUMULATE_PER_ITERATION')


class Trial(SettingsClient):

    def __init__(self, evalDir, index, trialSettings = None):
        '''
        Constructor
        Creates the required directories
        '''
        super().__init__()
        configured = False

        if os.path.isdir(evalDir):
            self.trialDir = os.path.join(evalDir, 'trial%03d' % index)
            if not os.path.exists(self.trialDir):
                os.mkdir(self.trialDir)
                os.chmod(self.trialDir, 0o775)
            logFile = os.path.join(self.trialDir, 'trial.log')
            os.close(os.open(logFile, os.O_CREAT | os.O_APPEND))
            os.chmod(logFile, 0o664)
        else:
            print("Trial %s: Directory not found" % evalDir)
            self.trialDir = None

        self.index = index
        self.storePerIteration = []
        self.storePerTrial = []

        if trialSettings is None:
            self.trialSettings = Settings('trialsettings')
        else:
            self.trialSettings = trialSettings.clone()

        self.settings = Settings('defaultSettings')
        SettingsManager.setRootSettings(self.settings)

        self.isFinished = False
        self.gitRevisionNumber = -1;
        random.seed(index)
        self.rngState = random.getstate()

    def store(self, name, value, mode=StoringType.STORE):
        '''
        Stores a piece of data. Multiple storage options are available.
        :param name: The name under which the data is stored
        :param value: The data
        :param mode: Can be either one of STORE_PER_ITERATION,
                     ACCUMULATE_PER_ITERATION, STORE, ACCUMULATE
        '''
        if mode is StoringType.STORE_PER_ITERATION:
            self.setProperty(name, value)
            if name not in self.storePerIteration:
                self.storePerIteration.append(name)
        elif mode is StoringType.ACCUMULATE_PER_ITERATION:
            if not isinstance(value, np.ndarray):
                value = np.array(value)
            if self.isProperty(name):
                    self.setProperty(name, np.vstack((self.getProperty(name),
                                                      value)))
            else:
                self.setProperty(name, value)
            if name not in self.storePerIteration:
                self.storePerIteration.append(name)
        elif mode is StoringType.ACCUMULATE:
            if not isinstance(value, np.ndarray):
                value = np.array(value)
            if self.isProperty(name):
                if isinstance(value, np.ndarray):
                    self.setProperty(name, np.vstack((self.getProperty(name),
                                                      value)))
            else:
                self.setProperty(name, value)
            if name not in self.storePerTrial:
                self.storePerTrial.append(name)
        elif mode is StoringType.STORE:
            self.setProperty(name, value)
            if name not in self.storePerTrial:
                self.storePerTrial.append(name)
        else: # pragma: no cover
            RuntimeError("Unknown StoringType")

    def isProperty(self, name):
        return hasattr(self, name)

    def setProperty(self, name, value):
        if not hasattr(self, name):
            setattr(self, name, value)
            self.linkProperty(name)
        else:
            self.setVar(name, value)
            # TODO: update the property in the settings?

    def getProperty(self, name):
        return getattr(self, name)

    def storeTrial(self, overwrite=True):
        return self.storeTrialInFile(self.trialDir, overwrite)

    def storeTrialInFile(self, trialDir, overwrite=True):
        '''
        Stores the trial in the given directory.
        Data and settings are stored separately.
        :param string filename: File name
        :param bool overwrite: Overwrite
        :return: True if storing is successful, False otherwise
        :rtpye: bool
        '''

        if trialDir is None or not os.path.isdir(trialDir):
            return False

        data = {}
        for name in self.storePerTrial:
            data[name] = self.getProperty(name)
        dataFile = os.path.join(trialDir, 'data.npy')

        if overwrite or not os.path.isfile(dataFile):
            np.save(dataFile, data)
        else:
            return False

        settingsFile = os.path.join(trialDir, 'settings.yaml')

        if overwrite or not os.path.isfile(settingsFile):

            self.trialSettings.store(settingsFile)

        else:
            return False

        trialFile = os.path.join(trialDir, 'trial.yaml')
        trialDict = dict()

        trialDict['isFinished'] = self.isFinished
        trialDict['rngState'] = self.rngState
        trialDict['gitRevisionNumber'] = self.gitRevisionNumber

        if overwrite or not os.path.isfile(trialFile):
            with open(trialFile, 'w') as stream:
                yaml.dump(trialDict, stream)


            return True
        else:
            return False

    def loadTrial(self):
        self.loadTrialFromFile(self.trialDir)

    def loadTrialFromFile(self, trialDir):
        '''
        Loads a trial from the given directory.
        :param trialDir: The directory of the trial to load
        '''
        print("Loading trial %s" % trialDir)
        if not os.path.isdir(trialDir):
            raise FileNotFoundError("Trial directory does not exist")
        settingsFile = os.path.join(trialDir, 'settings.yaml')
        dataFile = os.path.join(trialDir, 'data.npy')
        if not os.path.isfile(settingsFile):
            raise FileNotFoundError("Settings file not found")
        if not os.path.isfile(dataFile):
            raise FileNotFoundError("Data file not found")
        self.trialSettings.load(settingsFile)

        # resolve numpy crazyness with storing dictionary (wraps around and array)
        temp = np.load(dataFile)
        self.data = temp[()]
        for name,value in self.data.items():
            self.setProperty(name, value)

        trialFile = os.path.join(trialDir, 'trial.yaml')

        with open(trialFile, 'r') as stream:
            trialDict = yaml.load(stream)

        self.isFinished = trialDict['isFinished']
        self.rngState = trialDict['rngState']
        self.gitRevisionNumber = trialDict['gitRevisionNumber']

    def start(self, restart = False):
        if self.isFinished and not restart:
            print("Trial %s is already isFinished!" % self.trialDir)
        else:
            SettingsManager.setRootSettings(self.settings)

            commitCount = subprocess.getoutput(["git rev-list --count HEAD"])
            revNumber = subprocess.getoutput(["git rev-list --full-history --all | head -1"])
            date = subprocess.getoutput('date +%Y/%m/%d_%H:%M')

            self.gitRevisionNumber = commitCount + ':' + revNumber + ':' + date
            self.run()

            self.isFinished = True
            self.storeTrial()

    def applyTrialSettings(self):
        self.settings.copyProperties(self.trialSettings)

    def configure(self):
        raise NotImplementedError("Must be overwritten by subclass") # pragma: no cover

    def run(self):
        raise NotImplementedError("Must be overwritten by subclass") # pragma: no cover
