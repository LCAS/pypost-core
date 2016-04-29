from rlt.experiments.Experiment import Experiment


class ExperimentFromScript(Experiment):
    '''
    Creates a new experiment from a trial script.
    '''

    def __init__(self, rootDir, category, TrialClass):
        '''
        Constructor
        '''
        super(ExperimentFromScript, self).__init__(rootDir, category,
                                                   TrialClass.__name__)
        self.TrialClass = TrialClass
        self.defaultTrial = self.createTrial(self.path, 0)
        self.defaultSettings = self.defaultTrial.settings

    def createTrial(self, evalPath, trialIdx):
        '''
        Creates a new trial with given path and index.
        :param evalPath: Path of the evaluation
        :param trialIdx: Trial index
        :return: The newly created trial object
        '''
        return self.TrialClass(evalPath, trialIdx)
