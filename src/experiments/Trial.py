'''
Created on 26.01.2016

@author: Sebastian Kreutzer
'''
from common.Settings import Settings
from common import SettingsManager
import os
import traceback


class Trial(object):
    '''
    TODO: Documentation
    '''

    def __init__(self, evalDir, index):
        '''
        Constructor
        '''
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
        # TODO: Seed RNG here
        self.settings = Settings()
        self.isFinished = False
        self.preConfigure = True

    def storeTrial(self,):
        return self.storeTrialInFile('trial.mat')

    def storeTrialInFile(self, fileName, overwrite=True):
        # TODO: Store data in file
        # TODO: Store trial object in file
        raise RuntimeError("Not implemented")

    def configure(self, settings):
        self.settings.copyProperties(settings)
        self.preConfigure = False

    def start(self, withCatch=False, withProfiling=False):
        # FIXME: withProfiling is probably useless in python
        if self.isFinished:
            raise RuntimeError("Trial %s is already isFinished!" % self.trialDir)
        # TODO: Add diary equivalent
        SettingsManager.setRootSettings(self.settings) # FIXME: Not sure where self.settings is supposed to be defined...

        if withCatch:
            try:
                self.startInternal()
            except Exception:
                traceback.print_exc()
                # Log output
        else:
            self.startInternal()

        self.isFinished = True
        self.storeTrial()

    def startInternal(self):
        raise RuntimeError("Must be overwritten by the subclass")
