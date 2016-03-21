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

    # TODO: add __main__ method
    # Comment(Sebastian): __main__ should probably be added in inheriting
    #                     class. I don't think there's a good way to start
    #                     the trial from here.
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
            # Matlab prints trialDir here, but that doesn't make any sense
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
            if self.isProperty(name):
                if isinstance(value, np.ndarray):
                    self.setProperty(name, np.vstack((self.getProperty(name),
                                                      value)))
                else:
                    raise RuntimeError("The given value is not a ndarray.")
            else:
                self.setProperty(name, value)
            if name not in self.storePerIteration:
                self.storePerIteration.append(name)
        elif mode is StoringType.ACCUMULATE:
            if self.isProperty(name):
                if isinstance(value, np.ndarray):
                    self.setProperty(name, np.vstack((self.getProperty(name),
                                                      value)))
                else:
                    raise RuntimeError("The given value is not a ndarray.")
            else:
                self.setProperty(name, value)
            if name not in self.storPerTrial:
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
        return self.storeTrialInFile('trial', overwrite)

    def storeTrialInFile(self, fileName, overwrite=True):
        '''
        Stores the trial in the given file.
        Data and settings are stored separately.
        :param string filename: File name
        :param bool overwrite: Overwrite
        :return: True if storing is successful, False otherwise
        :rtpye: bool
        '''
        # TODO  Use filename
        if not self.trialDir:
            return
        
        data = {}
        for name in self.storePerTrial:
            data[name] = self.getProperty(name)
        dataFile = os.path.join(self.trialDir, 'data.npy')

        # Test this
        np.save(dataFile, data)

        settingsFile = os.path.join(self.trialDir, 'settings.yaml')
        if overwrite or not os.path.isfile(settingsFile):

            self.settings.store(settingsFile)

            return True
        return False

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
        raise RuntimeError("Must be overwritten by subclass")

    def run(self):
        raise RuntimeError("Must be overwritten by subclass")
