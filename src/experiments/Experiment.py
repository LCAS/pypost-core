import os
import getpass
import shutil
import re

import numpy as np

from common.Settings import Settings
from experiments.Evaluation import Evaluation


class Experiment(object):
    '''
    This class provides the basic functionality for defining experiments.
    An experiments is always a combination of a LearningSetup and a TaskSetup.
    For example, in order to learn ball i the cup for with parameter based
    REPS, we need a parameter based learning setup with the task setup from SL.
    For each experiment, we can define several evaluations. An evaluation is a
    specific setup of the parameter values of the algorithms. For example, we
    can define an evaluation, that performs 10 trials for different values of
    epsilon for REPS.
    '''

    # TODO(Sebastian): Find a reasonable root directory to store experiments
    # Comment(Sebastian): Current solution: Get root over constructor
    #root = 'Experiments/data'
    #root = os.getcwd()

    def __init__(self, rootDir, category, taskName):
        '''
        Constructor
        '''
        self.category = category

        self.evaluations = {}
        self.evaluationCollections = {}
        self.nodes = {}

        self.defaultTrial = None
        self.defaultSettings = Settings("defaultSettings")

        self.user = getpass.getuser()

        self.expId = []
        self.experimentId = -1

        self.evaluationIndexMap = dict()

        self.trialToEvaluationMap = {}
        self.trialIndexToDirectorymap = {}

        self.clusterJobs = {}

        self.taskName = taskName
        self.category = category

        self.path = os.path.join(rootDir, self.category, self.taskName)
        self.experimentPath = None

    @staticmethod
    def getByPath(self, path):
        fileName = os.path.join(path, "experiment.mat")
        '''
        FIXME
        load(fileName); <- can not be done in python
        return experiment
        '''
        raise RuntimeError("Not implemented")

    @staticmethod
    def loadFromDataBase(self, category, configurators, experimentID):
        expFileName = os.path.join(
            Experiment.root,
            category,
            self.taskName,
            "settings{03d}".format(experimentID),
            'experiment.mat')

        raise RuntimeError("Not implemented")
        '''
        FIXME
        load(expFileName);
        return experiment
        '''

    @staticmethod
    def addToDataBase(newExperiment):
        # TODO(Sebastian): There's some weird shit happening here and I don't
        # know if we can actually implement it like that in python
        if not os.path.exists(newExperiment.path):
            print("Creating directories for new experiment...")

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

        newExperiment.defaultTrial = newExperiment.createTrial(None,
            newExperiment.experimentPath, 0)
        newExperiment.defaultTrial.storeTrial()

        return newExperiment

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
        # TODO mathlab accessed self.evaluation (without "s"), does this
        # property exist? Is this function even in use?
        return self.evaluations[evalNumber]

    def getEvaluationIndex(self, evaluation):
        # TODO mathlab accessed self.evaluation (without "s"), does this
        # property exist? Is this function even in use?
        for idKey, evaluationVal in self.evaluations.items():
            if evaluationVal.evaluationName == evaluation.evaluationName:
                return idKey

        return None

    def resetTrials(self):
        for key, evaluation in self.evaluations.items():
            evaluation.resetTrials()

    def prepareDirectories(self):
        for key, evaluation in self.evaluations.items():
            self.createDirectories(evaluation)

    #:change: renamed from changePath to setPath
    def setPath(self, path):
        self.path = path

    def getTrialData(self, evaluationNumber=1):
        self.evaluations[evaluationNumber].getTrialData(self.path)

    def deleteExperiment(self):
        # I also like to live dangerously ( ͡° ͜ʖ ͡°)
        shutil.rmtree(self.path)

    def storeExperiment(self):
        '''
        FIXME python code:

        experiment = self;
        save(fullfile(self.experimentPath,'experiment'),'experiment','-v7.3');
        '''
        # TODO(Sebastian): Really not sure what to do here...
        # We can't serialize this object because there's to much stuff attached
        print('WARNING: Experiment.storeExperiment is not implemented!')
        #raise RuntimeError("Not implemented")

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

        # TODO why don't we already accept a settings object itself in the
        # arguments of this functions?
        evaluationSettings = self.defaultSettings.clone()

        properties = dict()
        i = 0
        for name in parameterNames:
            print(name)
            properties[name] = parameterValues[i]
            i += 1

        evaluationSettings.setProperties(properties)
        evaluationIndex = -1

        # check if the evaluation was already executed
        for key, evaluation in self.evaluations.items():
            if evaluation.settings.isSameSettings(evaluationSettings):
                evaluationIndex = i
                self.evaluationIndexMap[evaluationIndex] = evaluationIndex
                # FIXME there was a message 'Evaluation found with same
                # settings: %d\n, implement this later and use a log system
                return evaluation

        # find first "0" entry in index map and reserve it for this evaluation
        if evaluationIndex < 0:
            for key, val in self.evaluationIndexMap:
                if val == 0:
                    evaluationIndex = key
                    break

        evaluation = Evaluation(
            self,
            evaluationIndex,
            evaluationSettings,
            parameterNames,
            parameterValues,
            numTrials)
        self.evaluations[evaluationIndex] = evaluation
        self.evaluations[evaluationIndex].createFileStructure(True)

        self.storeExperiment()

        return evaluation

    def addEvaluationCollection(
            self, parameterNames, parameterValues, numTrials):
        '''
        Adds a collection of evaluations to the experiment, one for each parameterValue.
        :param parameterNames: A list of parameter names
        :param parameterValues: A list of parameter values
        :param numTrials: The number of trials
        '''
        evaluations = []
        for i in range(0, len(parameterValues) - 1):
            # TODO matlab code accessed "evaluations{i}" which was nowhere initialized. is this code still in use?
            # TODO matlab accessed values like this: {parameterValues[i,...]}
            # this should be equal to list(parameterValues[i]) but recheck this
            evaluations.append(
                self.addEvaluation(
                    parameterNames,
                    list(
                        parameterValues[i]),
                    numTrials))

        evaluationCollection = EvaluationCollection(
            self,
            evaluations,
            parameterNames,
            parameterValues)
        self.evaluationCollections.append(evaluationCollection)

        self. storeExperiment()

        return evaluationCollection

    '''
    Loads the trials with the given ID from file system.
    :param int trialID: The ID of the trial to load
    :return: The loaded trial
    :rtype: experiments.Trial
    '''

    def loadTrialFromID(self, trialID):
        trialName = os.path.join(
            self.trialIndexToDirectorymap[trialID],
            'trial.mat')
        print('WARNING: Experiment.loadFromDataBase is not implemented.')
        #raise RuntimeError("Not implemented")
        '''
        FIXME matlab code:
        load(trialName);
        '''
        #return trial

    '''
    Returns the number of trials.
    :return: The number of trials
    :rtype: int
    '''

    def getNumTrials(self):
        return len(self.trialIndexToDirectorymap)

    '''
    Executes the experiment on the local machine.

    :param list trialIndices: A list containg the indices of the trials to run.
                              If None, all trials are executed.
    '''

    def startLocal(self, trialIndices=None):
        if not trialIndices:
            trialIndices = self.trialIndexToDirectorymap

        for key in trialIndices:
            print('Starting Trial {0} locally\n'.format(key))

            trial = Experiment.loadTrialFromID(self, key)
            trial.start()

    '''
    Returns a list of trial IDs.
    :return: The trial list.
    :rtype: list of integers
    '''

    def getTrialIDs(self):
        return self.trialIndexToDirectorymap.keys()

    def startBatch(self, **args):
        # TODO recheck the type if args
        self.startBatchTrials(self.getTrialIDs(), **args)

    def startBatchTrials(
            self, trialIDs, numParallelJobs, jobsPerNode, computationTime):
        # FIXME implement this
        raise RuntimeError("Not implemented")

    def createLSFFullNode(
            self, clusterJobID, numParallelJobs, jobsPerNode, computationTime):
        # FIXME implement this
        raise RuntimeError("Not implemented")

    def startCluster(self, clusterJobID, jobID):
        trialIndices = self.clusterJobs[clusterJobID]
        # FIXME use a log system
        print(
            'Starting Trial {0} on the cluster\n'.format(
                trialIndices[jobID]))

        trial = self.loadTrialFromID(trialIndices[jobID])
        trial.start()

    def setDefaultParameter(self, parameterName, parameterValue):
        # TODO matlab code was comparing for inequality (strcomp()==0) . i changed it since
        # it seems that "settings." prefixes should get removed from parameter
        # names
        if parameterName[0:9] == "settings.":
            parameterName = parameterName[10:]

        self.defaultSettings.set(parameterName, parameterValue)

    def createTrial(self, settings, evalPath, trialIndex):
        raise NotImplementedError("Abstract Method")
