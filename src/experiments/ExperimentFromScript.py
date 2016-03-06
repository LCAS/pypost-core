from experiments.Experiment import Experiment
from experiments.TrialFromScript import TrialFromScript
from common.Settings import Settings


class ExperimentFromScript(Experiment):
    '''
    FIXME:
    No documentation available yet.
    Please take this opportunity to think about the vastness of the universe
    and the insignificance of human life.
    How do you feel? If you like, write about your experience
    in your diary or draw a picture.
    Now carry on.
    '''

    def __init__(self, category, scriptName):
        '''
        Constructor
        '''
        super(Experiment, self).__init__(category, scriptName)
        self.scriptName = scriptName
        self.defaultTrial = self.createTrial(Settings(), self.path, 0)
        self.defaultSettings = self.defaultTrial.settings

    def createTrial(self, settings, evalPath, trialIdx):
        return TrialFromScript(settings, evalPath, trialIdx, self.scriptname)
