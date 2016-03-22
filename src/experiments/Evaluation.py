import os


class Evaluation():
    '''
    classdocs
    '''

    def __init__(self, experiment, evaluationID, settings, parameterNames,
                 parameterValues, numTrials=1):
        '''
        Constructor
        '''
        self.numTrials = numTrials
        self.evaluationID = evaluationID
        self.parameterNames = parameterNames
        self.parameterValues = parameterValues
        self.settings = settings
        self.setExperiment(experiment, evaluationID)

    def setExperiment(self, experiment, evaluationID):
        self.evaluationName = 'eval%03d' % evaluationID
        self.path = os.path.join(experiment.path, self.evaluationName)
        self.experiment = experiment

    def createFileStructure(self, overwrite):
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        settingsPath = os.path.join(self.path, 'settings.yaml')
        self.settings.store(settingsPath)

        print("Creating evaluation file structure for evaluation in %s" %
              self.path)
        for i in range(0, self.numTrials):
            trialPath = os.path.join(self.path, 'trial%03d' % i)
            if not os.path.isfile(os.path.join(trialPath, 'trial')):
                trial = self.experiment.createTrial(self.settings,
                                                    self.path, i)
                trial.storeTrial(overwrite)
                trial.storeTrialInFile('initialTrial')
            self.experiment.registerTrial(self, trialPath)

        for root, dirs, files in os.walk(self.path):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o775)
            for f in files:
                os.chmod(os.path.join(root, f), 0o775)
