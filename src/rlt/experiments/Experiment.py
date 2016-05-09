import os
import getpass
import shutil
import re

import numpy as np

from rlt.common.Settings import Settings
from rlt.experiments.Evaluation import Evaluation
from rlt.experiments.Trial import Trial


class Experiment(object):
    '''
    This class provides the basic functionality for defining experiments.
    An experiments is always a combination of a LearningSetup and a TaskSetup.
    For example, in order to learn ball in the cup for with parameter based
    REPS, we need a parameter based learning setup with the task setup from SL.
    For each experiment, we can define several evaluations. An evaluation is a
    specific setup of the parameter values of the algorithms. For example, we
    can define an evaluation, that performs 10 trials for different values of
    epsilon for REPS.
    '''

    def __init__(self, rootDir, category, taskName):
        '''
        Constructor
        '''
        self.category = category

        self.evaluations = {}

        self.defaultTrial = None
        self.defaultSettings = Settings("defaultSettings")

        self.user = getpass.getuser()

        self.experimentId = -1

        self.trialToEvaluationMap = {}
        self.trialIndexToDirectorymap = {}

        self.clusterJobs = {}

        self.taskName = taskName
        self.category = category

        self.path = os.path.join(rootDir, self.category, self.taskName)
        self.experimentPath = None

    def create(self):
        while not os.path.exists(self.path):
            path = self.path
            while not os.path.exists(os.path.abspath(os.path.join(path, os.pardir))): #pragma: no cover
                path = os.path.abspath(os.path.join(path, os.pardir))
            os.mkdir(path)

        maxId = -1
        for file in os.listdir(self.path):
            filePath = os.path.join(self.path, file)
            if os.path.isdir(filePath) \
               and os.path.basename(file).startswith('experiment'):
                currentId = int(file[10:13])
                maxId = max(currentId, maxId)
                otherSettings = Settings("other")
                otherSettings.load(os.path.join(filePath, 'settings.yaml'))
                if self.defaultSettings.isSameSettings(otherSettings):
                    print("Experiment with same settings found")
                    self.experimentId = currentId
                    self.experimentPath = filePath
                    self.load()
                    return

        self.experimentId = maxId+1
        self.experimentPath = os.path.join(
            self.path, ('experiment%03d' % self.experimentId))
        if not os.path.exists(self.experimentPath): #pragma: no cover
            os.mkdir(self.experimentPath)
        self.defaultSettings.store(os.path.join(self.experimentPath,
                                                "settings.yaml"))

    '''
    @staticmethod
    def addToDataBase(newExperiment):
        while not os.path.exists(newExperiment.path):
            path = newExperiment.path
            while not os.path.exists(os.path.abspath(os.path.join(path, os.pardir))):
                path = os.path.abspath(os.path.join(path, os.pardir))
            os.mkdir(path)


        experimentId = -1

        for file in os.listdir(newExperiment.path):
            if os.path.isdir(file) and os.path.dirname(file).startswith('settings'):
                id = re.findall(r'\d', os.path.dirname(file))[0]
                print("Found existing experiment")
                experimentFileName = os.path.join(file, 'experiment.npy')
                # TODO(Sebastian): Load experiment here and check if settings are equivalent
                # If they are, set the id to that experiment's id
                # Else, mark index as "free"
                # This might not actually sense here since we can't just save
                # the whole object
                experimentId = id

        if experimentId == -1:
            # FIXME(Sebastian): Find first free index
            experimentId = 0

        newExperiment.experimentPath = os.path.join(
            newExperiment.path, 'settings%03d' % experimentId)
        if not os.path.exists(newExperiment.experimentPath):
            os.mkdir(newExperiment.experimentPath)

        newExperiment.defaultTrial = newExperiment.createTrial(
            newExperiment.experimentPath, 0)
        newExperiment.defaultTrial.storeTrial()

        return newExperiment
    '''

    def load(self):
        pass

    def startDefaultTrial(self):
        self.defaultTrial.start()

    def registerTrial(self, evaluation, trialDir):
        if not self.trialToEvaluationMap:
            trialId = 0
        else:
            trialId = max(self.trialToEvaluationMap.keys()) + 1

        self.trialToEvaluationMap[trialId] = evaluation
        self.trialIndexToDirectorymap[trialId] = trialDir

    def getEvaluation(self, evalNumber):
        return self.evaluations[evalNumber]

    def getEvaluationIndex(self, evaluation):
        for idKey, evaluationVal in self.evaluations.items():
            if evaluationVal.evaluationName == evaluation.evaluationName:
                return idKey

        return None

    def deleteExperiment(self):
        shutil.rmtree(self.path)

    def addEvaluation(self, parameterNames, parameterValues, numTrials):
        '''
        Adds a new evaluation to the experiment.
        This is only for a single evaluation. Please use evaluation collections for multiple ones
        :param list parameterNames: A list of parameter names
        :param list parameterValues: A list of parameter values
        :param int numTrials: The number of trials
        '''
        if len(parameterValues) != 1:
            raise RuntimeError(
                "Only a single parameter is accepted by this method")

        evaluationSettings = self.defaultSettings.clone()

        properties = dict()
        i = 0
        for name in parameterNames:
            properties[name] = parameterValues[i]
            i += 1

        evaluationSettings.setProperties(properties)
        evaluationIndex = -1

        for key, evaluation in self.evaluations.items():
            if evaluation.settings.isSameSettings(evaluationSettings):
                evaluationIndex = i
                print("Evaluation found with same settings")
                return evaluation

        evaluationIndex = len(self.evaluations)

        evaluation = Evaluation(
            self,
            evaluationIndex,
            evaluationSettings,
            parameterNames,
            parameterValues,
            numTrials)
        self.evaluations[evaluationIndex] = evaluation
        self.evaluations[evaluationIndex].createFileStructure(True)

        return evaluation

    def addEvaluationCollection(
            self, parameterNames, parameterValues, numTrials):
        '''
        Adds a collection of evaluations to the experiment,
        one for each parameterValue.
        :param parameterNames: A list of parameter names
        :param parameterValues: A list of parameter values
        :param numTrials: The number of trials
        '''
        evaluations = []
        for i in range(0, len(parameterValues)):
            evaluations.append(
                self.addEvaluation(
                    parameterNames,
                    [parameterValues[i]],
                    numTrials))

        return evaluations

    def loadTrialFromID(self, trialID):
        '''
        Loads the trials with the given ID from file system.
        :param int trialID: The ID of the trial to load
        :return: The loaded trial
        :rtype: experiments.Trial
        '''
        if trialID not in self.trialIndexToDirectorymap:
            raise KeyError("Trial not found")
        trialDir = self.trialIndexToDirectorymap[trialID]
        print("Loading trial %s" % trialDir)
        trial = self.createTrial(os.path.abspath(
                                    os.path.join(trialDir, os.path.pardir)),
                                 trialID)
        trial.loadTrial()
        return trial

    def getNumTrials(self):
        '''
        Returns the number of trials.
        :return: The number of trials
        :rtype: int
        '''
        return len(self.trialIndexToDirectorymap)

    def startLocal(self, trialIndices=None):
        '''
        Executes the experiment on the local machine.
        :param trialIndices: A list containg the indices of the trials to run.
                              If None, all trials are executed.
        '''
        if not trialIndices:
            trialIndices = self.trialIndexToDirectorymap

        for key in trialIndices:
            print('Starting Trial {0} locally\n'.format(key))

            trial = Experiment.loadTrialFromID(self, key)
            trial.start()

    def getTrialIDs(self):
        '''
        Returns a list of trial IDs.
        :return: The trial list.
        :rtype: list of integers
        '''
        return self.trialIndexToDirectorymap.keys()

    def setDefaultParameter(self, parameterName, parameterValue):
        if parameterName[0:9] == "settings.":
            parameterName = parameterName[9:]

        self.defaultSettings.setProperty(parameterName, parameterValue)

    def createTrial(self, evalPath, trialIndex):
        raise NotImplementedError("Abstract Method") # pragma: no cover
