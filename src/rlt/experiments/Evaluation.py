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
        print("Directory is %s" % self.path)

    def setExperiment(self, experiment, evaluationID):
        self.evaluationName = 'eval%03d' % evaluationID
        self.path = os.path.join(experiment.experimentPath, self.evaluationName)
        self.experiment = experiment

    def createFileStructure(self, overwrite):
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        settingsPath = os.path.join(self.path, 'settings.yaml')
        self.settings.store(settingsPath)

        for i in range(0, self.numTrials):
            trialPath = os.path.join(self.path, 'trial%03d' % i)
            if not os.path.isfile(os.path.join(trialPath, 'data.npy')):
                trial = self.experiment.createTrial(self.path, i)
                trial.storeTrial(overwrite)
                trial.storeTrialInFile('initialTrial')
            else:
                print("Found existing trial %03d, not recreating" % i)
            self.experiment.registerTrial(self, trialPath)

        for root, dirs, files in os.walk(self.path):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o775)
            for f in files:
                os.chmod(os.path.join(root, f), 0o775)
