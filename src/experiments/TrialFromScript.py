'''
Created on 26.01.2016

@author: Sebastian Kreutzer
'''

from experiments.Trial import Trial


class TrialFromScript(Trial):
    '''
    TODO: Documentation
    '''

    def __init__(self, settingsEval, evalDir, trialIdx, scriptName):
        '''
        Constructor
        '''
        super(Trial, self).__init__(evalDir, trialIdx)
        self.scriptName = scriptName
        raise RuntimeError("Not fully implemented")

    def saveWorkspace(self):
        raise RuntimeError("Not implemented")

    def loadWorkspace(self):
        raise RuntimeError("Not implemented")

    def storeTrial(self):
        self.saveWorkspace()
        super(Trial, self).storeTrial()

    def startInternal(self):
        self.isConfigure = False
        self.isStart = True

        exec(compile(open(self.scriptName, "rb").read(),
                     self.scriptName, 'exec'))

        
        