import yaml
import os
from  pypost.common.SettingsClient import SettingsClient
from  pypost.common.SettingsManager import setRootSettings
from  pypost.common.Settings import Settings


class Evaluation(SettingsClient):
    '''
    classdocs
    '''

    def __init__(self, experiment, evaluationID, settings, parameterNames = None,
                 parameterValues = None, numTrials=1):
        '''
        Constructor
        '''
        SettingsClient.__init__(self)

        self.numTrials = numTrials
        self.evaluationID = evaluationID
        self.parameterNames = parameterNames
        self.parameterValues = parameterValues
        self.globalTrialIDs = []


        if isinstance(settings, str):
            self.settings = Settings('evaluation')
            self.settings.load(os.path.join(settings, 'settings.yaml'))
            setRootSettings(self.settings)

            with open(os.path.join(settings, 'eval.yaml'), 'r') as stream:
                evalSettings = yaml.load(stream)

            self.numTrials = evalSettings['numTrials']
            self.parameterNames = evalSettings['parameterNames']
            self.parameterValues = evalSettings['parameterValues']

        else:
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
        evalPath = os.path.join(self.path, 'eval.yaml')

        self.settings.store(settingsPath)
        dataToStore = dict()
        dataToStore['numTrials'] = self.numTrials
        dataToStore['parameterNames'] = self.parameterNames
        dataToStore['parameterValues'] = self.parameterValues

        with open(evalPath, 'w') as stream:
            yaml.dump(dataToStore, stream)

        for i in range(0, self.numTrials):
            trialPath = os.path.join(self.path, 'trial%03d' % i)
            if not os.path.isfile(os.path.join(trialPath, 'data.npy')):
                trial = self.experiment.createTrial(self.path, i, self.settings)
                trial.storeTrial(overwrite)
            else:
                print("Found existing trial %03d, not recreating" % i)
            trialId = self.experiment.registerTrial(self, trialPath)
            self.globalTrialIDs.append(trialId)

        for root, dirs, files in os.walk(self.path):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o775)
            for f in files:
                os.chmod(os.path.join(root, f), 0o775)

    def loadTrialFromID(self, trialID):
        globalID = self.globalTrialIDs[trialID]
        return self.experiment.loadTrialFromID(globalID)

    def getNumTrials(self):
        return len(self.globalTrialIDs)