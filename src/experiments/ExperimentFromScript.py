from experiments.Experiment import Experiment


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

    def __init__(self, rootDir, category, TrialClass):
        '''
        Constructor
        '''
        super(ExperimentFromScript, self).__init__(rootDir, category,
                                                   TrialClass.__name__)
        self.TrialClass = TrialClass
        self.defaultTrial = self.createTrial(None, self.path, 0)
        self.defaultSettings = self.defaultTrial.settings

    def createTrial(self, settings, evalPath, trialIdx):
        '''
        Creates a new trial with given path and index.
        :param evalPath: Path of the evaluation
        :param trialIdx: Trial index
        :return: The newly created trial object
        '''
        return self.TrialClass(evalPath, trialIdx)
