'''
Created on 26.01.2016

@author: Sebastian Kreutzer
'''
import os
import getpass
import shutil

import numpy as np

from Experiments import Evaluation


class Experiment(object):
    '''
    TODO: Document this shit
    '''

    root = 'Experiments/data'

    def __init__(self, category, taskName):
        '''
        Constructor
        '''
        self.category = category

        self.evaluations = {}
        self.evaluationCollections = {}
        self.nodes = {}

        self.defaultTrial = None
        self.defaultSettings = None  # FIXME create Settings instance

        self.user = getpass.getuser()

        self.expId = []
        self.experimentId = -1

        self.evaluationIndexMap = np.empty((100, 1))
        self.evaluationIndexMap.fill(-1)

        self.trialToEvaluationMap = {}
        self.trialIndexToDirectorymap = {}

        self.clusterJobs = {}

        self.taskName = taskName
        self.category = category

        self.path = os.path.join(Experiment.root, self.category, self.taskName)
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

    def addToDataBase(self, newExperiment):
        raise RuntimeError("Not implemented")

        '''
        FIXME implement this
        function [experiment] = addToDataBase(newExperiment)
            obj = newExperiment;
            [st, msg, msgId] = mkdir(obj.path);
            d = dir(obj.path);
            isub = [d(:).isdir];
            nameFolds = {d(isub).name}';

            experimentId = -1;
            experimentIdVec = true(100,1);
            for i = 1:length(nameFolds)
                if (length(nameFolds{i}) > 7 && strcmp(nameFolds{i}(1:8), 'settings'))
                    lId = sscanf(nameFolds{i}, 'settings%03d');
                    expFileName = fullfile(obj.path, sprintf('settings%03d', lId), 'experiment.mat');

                    load(expFileName);
                    [sameDefaultSettings, differentParameters] = obj.defaultSettings.isSameSettings(experiment.defaultSettings);
                    fprintf('Checking Experiment ID %d: ', lId);
                    if (sameDefaultSettings)
                        experimentId = lId;
                        fprintf('Found same experiment\n');
                        return;
                    else
                        experimentIdVec(lId) = false;
                        fprintf('Different Settings, differences are in');
                        differentParameters
                    end
                end
            end
            if (experimentId == -1)
                experimentId = find(experimentIdVec, 1);
                fprintf('Create New Experiment with ID %d\n', experimentId);
            end
            obj.experimentId = experimentId;
            obj.experimentPath = fullfile(obj.path, sprintf('settings%03d', obj.experimentId));
            [st, msg, msgId] = mkdir(obj.experimentPath);


            %Recreate default trial with new default settings
            obj.defaultTrial = Experiments.Trial.createTrialFromConfigurators(obj.defaultSettings, obj.experimentPath, 0, obj.configurators, obj.evalCriterion, 100);
            %obj.defaultSettings = obj.defaultTrial.settings;
            obj.defaultTrial.storeTrial();

            experiment = obj;
            obj.storeExperiment();
        end
        '''

    def startDefaultTrial(self):
        self.defaultTrial.start()

    def registerTrial(self, evaluation, trialDir):
        if not self.trialToEvaluationMap:
            trialId = 0
        else:
            trialId = self.trialToEvaluationMap[
                max(self.trialToEvaluationMap, key=self.trialToEvaluationMap.get)] + 1

        self.trialToEvaluationMap[trialId] = evaluation
        self.trialIndexToDirectorymap[trialId] = trialDir

    def getEvaluation(self, evalNumber):
        # TODO mathlab accessed obj.evaluation (without "s"), does this
        # property exist? Is this function even in use?
        return self.evaluations[evalNumber]

    def getEvaluationIndex(self, evaluation):
        # TODO mathlab accessed obj.evaluation (without "s"), does this
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

    #@change renamed from changePath to setPath
    def setPath(self, path):
        self.path = path

    def getTrialData(self, evaluationNumber=1):
        self.evaluations[evaluationNumber].getTrialData(self.path)

    def deleteExperiment(self):
        shutil.rmtree(self.path)

    def storeExperiment(self):
        '''
        FIXME python code:

        experiment = obj;
        save(fullfile(obj.experimentPath,'experiment'),'experiment','-v7.3');
        '''
        raise RuntimeError("Not implemented")

    def addEvaluation(self, parameterNames, parameterValues, numTrials):
        '''
        This is only for a single evaluation. Please use evaluation collections for multiple ones
        '''
        if len(parameterValues) != 1:
            raise RuntimeError(
                "Only a single parameter is accepted by this method")

        # TODO why don't we already accept a settings object itself in the
        # arguments of this functions?
        evaluationSettings = self.defaultSettings.clone()
        evaluationSettings.setProperties(parameterNames, parametervalues)
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
            for key, val in evaluationIndexMap.iteritems():
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
        self.evaluations[evaluationIndex].createDirectories(true)

        self.storeExperiment()

        return evaluation

    def addEvaluationCollection(
            self, parameterNames, parameterValues, numTrials):
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

    def loadTrialFromID(self, trialID):
        trialName = os.path.join(
            self.trialIndexToDirectorymap[trialID],
            'trial.mat')
        raise RuntimeError("Not implemented")
        '''
        FIXME matlab code:
        load(trialName);
        '''
        return trial

    def getNumTrials(self):
        return len(self.trialIndexToDirectorymap)

    def startLocal(self, trialIndices=None):
        if not trialIndices:
            trialIndices = self.trialIndexToDirectorymap.keys()

        for i in range(0, len(trialIndices) - 1):
            # FIXME use a log system
            print('Starting Trial {0} locally\n'.format(trialIndices[i]))

            trial = Experiment.loadTrialFromID(self, trialIndices[i])
            trial.start()

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
