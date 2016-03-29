from common.Settings import Settings
from common import SettingsManager
import sys
import os
import random
import traceback
import numpy as np
from enum import Enum

StoringType = Enum('StoringType', 'STORE, STORE_PER_ITERATION, ACCUMULATE, '
                   'ACCUMULATE_PER_ITERATION')


class Trial():
    '''
    TODO: Documentation
    '''

    def __init__(self, evalDir, index):
        '''
        Constructor
        '''
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
        self.properties = {}
        self.storePerIteration = []
        self.storePerTrial = []
        self.settings = Settings('trialsettings')
        self.isFinished = False
        random.seed(index)
        self.rngState = random.getstate()
        self.configure()

    def store(self, name, value, mode=StoringType.STORE):
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
        else:
            RuntimeError("Unknown StoringType")

    def isProperty(self, name):
        return name in self.properties

    def setProperty(self, name, value):
        self.properties[name] = value

    def getProperty(self, name):
        return self.properties[name]

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

            self.settings.store(settingsFile)

            return True
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
        self.settings.load(settingsFile)
        # FIXME(Sebastian): Load data too?
        data = np.load(dataFile)

    def start(self, withCatch=False, withProfiling=False):
        # FIXME: withProfiling is probably useless in python
        if self.isFinished:
            raise RuntimeError("Trial %s is already isFinished!" % self.trialDir)
        # TODO: Add diary equivalent
        SettingsManager.setRootSettings(self.settings)

        if withCatch:
            try:
                self.run()
            except Exception:
                traceback.print_exc()
                # Log output
        else:
            self.run()

        self.isFinished = True
        self.storeTrial()

    def configure(self):
        raise NotImplementedError("Must be overwritten by subclass")

    def run(self):
        raise NotImplementedError("Must be overwritten by subclass")
