'''
Created on 26.01.2016

@author: Sebastian Kreutzer
'''
from common.Settings import Settings
from common import SettingsManager
import os


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
