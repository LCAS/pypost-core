from common.Settings import Settings
from common import SettingsManager
import os
import traceback
import numpy as np
from enum import Enum
from nose.util import isproperty

StoringType = Enum('StoringType', 'STORE, STORE_PER_ITERATION, ACCUMULATE, '
                   'ACCUMULATE_PER_ITERATION')


class Trial(object):
    '''
    TODO: Documentation
    '''

    # TODO: add __main__ method

    def __init__(self, evalDir, index):
        '''
        Constructor
        '''
        # What use do these two lines have?
        settingsTrial = Settings('new')
        SettingsManager.setRootSettings(settingsTrial) # FIXME: Not implemented

        if os.path.isdir(evalDir):
            self.trialDir = os.path.join(evalDir, 'trial%03d' % index)
            os.mkdir(self.trialDir)
            os.chmod(self.trialDir, 0o775)
            logFile = os.path.join(self.trialDir, 'trial.log')
            os.close(os.open(logFile, 'a'))
            os.chmod(logFile, 0o664)
        else:
            # Matlab prints trialDir here, but that doesn't make any sense
            print("Trial %s: Directory not found" % self.evalDir)

        self.index = index
        self.properties = {}
        self.storePerIteration = []
        self.storePerTrial = []
        # TODO: Seed RNG here
        self.settings = Settings()
        self.isFinished = False
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
                    raise RuntimeError("Well shit...")
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
                    raise RuntimeError("Well shit...")
            else:
                self.setProperty(name, value)
            if name not in self.storPerTrial:
                self.storePerTrial.append(name)
        elif mode is StoringType.STORE_PER_ITERATION:
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
        data = {}
        for name in self.storePerTrial:
            data[name] = self.getProperty(name)
        dataFile = os.path.join(self.trialDir, 'data')

        # TODO: Serialize data

        storeFile = os.path.join(self.trialDir, fileName)
        if overwrite or not os.path.isfile(storeFile):

             # TODO: Store trial object in file

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
        # TODO: this is not needed any more
        raise RuntimeError("Must be overwritten by subclass")

    def run(self):
        raise RuntimeError("Must be overwritten by subclass")
