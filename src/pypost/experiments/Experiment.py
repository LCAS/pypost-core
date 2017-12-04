import os
import getpass
import shutil
import numpy as np
import stat
import itertools

from pypost.common.SettingsManager import setRootSettings
from pypost.experiments.Evaluation import Evaluation
from pypost.data.DataManager import DataManager

import yaml, subprocess, os, time, random, os.path

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

    def __init__(self, rootDir, category, TrialClass, create = True):
        '''
        Constructor
        '''


        self.category = category

        self.evaluations = {}



        self.user = getpass.getuser()

        self.experimentId = -1

        self.trialToEvaluationMap = {}
        self.trialIndexToDirectorymap = {}

        self.clusterJobs = {}

        self.taskName = TrialClass.__name__
        self.category = category

        self.path = os.path.join(rootDir, self.category, self.taskName)
        while not os.path.exists(self.path):
            path = self.path
            while not os.path.exists(os.path.abspath(os.path.join(path, os.pardir))):  # pragma: no cover
                path = os.path.abspath(os.path.join(path, os.pardir))
            os.mkdir(path)

        self.experimentPath = None

        self.TrialClass = TrialClass
        self.defaultTrial = self.createTrial(self.path, 0)
        self.defaultTrial.configure()
        if (create):
            self.defaultTrial.storeTrial(True)
        self.defaultSettings = self.defaultTrial.settings
        self.rootDir = rootDir
        self.maxId = -1

    def load(self, experimentId = 'last'):
        '''

        :param experimentId: desired ID of the experiment (for loading old experiments). If ID equals -1, new experiment
        is autmatically created
        :return:
        '''
        while not os.path.exists(self.path):
            path = self.path
            while not os.path.exists(os.path.abspath(os.path.join(path, os.pardir))): #pragma: no cover
                path = os.path.abspath(os.path.join(path, os.pardir))
            os.mkdir(path)

        self.maxId = -1
        for file in os.listdir(self.path):
            filePath = os.path.join(self.path, file)
            if os.path.isdir(filePath) \
               and os.path.basename(file).startswith('experiment'):
                currentId = int(file[10:13])
                self.maxId = max(currentId, self.maxId)

                if currentId == experimentId:
                    print("Experiment with same settings found")
                    self.experimentId = currentId
                    self.experimentPath = filePath
                    self._load()
                    return True

        if (experimentId == 'last' and self.maxId >= 0):
            print('Reusing last experiment...(%03d)' % self.maxId)
            self.experimentId = self.maxId
            self.experimentPath = os.path.join(self.path, ('experiment%03d' % self.maxId))
            self._load()
            return True
        else:
            return False



    def create(self, experimentId = 'last', copyCWD=False):
        '''

        :param experimentId: desired ID of the experiment (for loading old experiments). If ID equals -1, new experiment
        is autmatically created
        :param bool copyCWD: copy current working directory to experiment path
        :return:
        '''
        result = self.load(experimentId)

        if not result:
            print("Create new experiment...")
            self.experimentId = self.maxId+1
            self.experimentPath = os.path.join(
                self.path, ('experiment%03d' % self.experimentId))
            if not os.path.exists(self.experimentPath): #pragma: no cover
                os.mkdir(self.experimentPath)

            if copyCWD:
                run_folder = os.getcwd()
                target_folder = self.experimentPath + '/code'
                self.copy_code_folder(run_folder, target_folder, symlinks=True, ignore='.*')

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

    def _load(self):
        dirList = os.listdir(self.experimentPath)
        dirList.sort()
        for file in dirList:
            filePath = os.path.join(self.experimentPath, file)
            if os.path.isdir(filePath) \
                    and os.path.basename(file).startswith('eval'):

                evaluationIndex = int(file[-2:])

                evaluation = Evaluation(
                    self,
                    evaluationIndex,
                    filePath)
                self.evaluations[evaluationIndex] = evaluation
                self.evaluations[evaluationIndex].createFileStructure(True)

    def startDefaultTrial(self):
        self.defaultTrial.start()

    def registerTrial(self, evaluation, trialDir):
        if not self.trialToEvaluationMap:
            trialId = 0
        else:
            trialId = max(self.trialToEvaluationMap.keys()) + 1

        self.trialToEvaluationMap[trialId] = evaluation
        self.trialIndexToDirectorymap[trialId] = trialDir

        return trialId

    def getEvaluation(self, evalNumber):
        return self.evaluations[evalNumber]

    def getEvaluationList(self):
        return list(self.evaluations.values())

    def getEvaluationIndex(self, evaluation):
        for idKey, evaluationVal in self.evaluations.items():
            if evaluationVal.evaluationName == evaluation.evaluationName:
                return idKey

        return None

    def deleteAllExperiments(self):
        try:
            shutil.rmtree(self.path)
        except Exception as error:
            pass
        self.experimentId = -1

    def deleteExperiment(self):
        try:
            shutil.rmtree(self.experimentPath)
        except Exception as error:
            pass
        self.evaluations = {}


    def addEvaluation(self, parameterNames, parameterValues, numTrials):
        '''
        Adds a new evaluation to the experiment.
        This is only for a single evaluation. Please use evaluation collections for multiple ones
        :param list parameterNames: A list of parameter names
        :param list parameterValues: A list of parameter values
        :param int numTrials: The number of trials
        '''
        # if len(parameterValues) != 1:
        #     raise RuntimeError(
        #         "Only a single parameter is accepted by this method")

        evaluationSettings = self.defaultSettings.clone()

        properties = dict()
        i = 0
        for name, value in zip(parameterNames, parameterValues):
            properties[name] = value
            i += 1

        evaluationSettings.setProperties(properties)
        setRootSettings(evaluationSettings)
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

    def getEvaluationsFromQuery(self, propertyDictionary):
        evaluationsQuery = []
        for i in range(0, len(self.evaluations)):
            if self.evaluations[i].settings.querySettings(propertyDictionary):
                evaluationsQuery.append(self.evaluations[i])

        return evaluationsQuery

    def addEvaluationCollection(
            self, parameterDict, numTrials, combinations=False):
        '''
        Adds a collection of evaluations to the experiment,
        one for each parameterValue.
        :param parameterDict: A dictionary of parameter name keys and parameter values of the form
        {key1: [k1v1, k1v2, ...], key2: [k2v1, k2v2, ...], ...}. If combinations == False each list of values has to be
        of same length
        :param combinations: If true, the cartesian product of all parameter keys and values will be evaluated
        :param numTrials: The number of trials
        '''
        evaluations = []
        parameterNames = list(parameterDict.keys())
        parameterValues = list(parameterDict.values())
        if combinations:
            parameterValues = list(itertools.product(*parameterValues))
        else:
            parameterValues = list(zip(*parameterValues))
        for parameterValue in parameterValues:
            evaluations.append(
                self.addEvaluation(
                    parameterNames,
                    parameterValue,
                    numTrials))

        return evaluations

    def loadTrialFromID(self, trialIDglobal):
        '''
        Loads the trials with the given ID from file system.
        :param int trialID: The ID of the trial to load
        :return: The loaded trial
        :rtype: experiments.Trial
        '''
        if trialIDglobal not in self.trialIndexToDirectorymap:
            raise KeyError("Trial not found")
        trialDir = self.trialIndexToDirectorymap[trialIDglobal]
        #print("Loading trial %s" % trialDir)
        trialIDeval = int(trialDir.split('/')[-1][-2:])
        trial = self.createTrial(os.path.abspath(os.path.join(trialDir, os.path.pardir)),trialIDeval)
        trial.loadTrial()
        return trial

    def getNumTrials(self):
        '''
        Returns the number of trials.
        :return: The number of trials
        :rtype: int
        '''
        return len(self.trialIndexToDirectorymap)

    def startLocal(self, trialIndices=None, restart = False):
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

            trial.start(restart = restart)

    def startSLURM(self, trialIndices = None, restart = False,
                   numParallelJobs=20, memory = 5000, computationTime= 23 * 60 + 59,
                   accelerator=""):

        if not trialIndices:
            trialIndices = list(self.trialIndexToDirectorymap.keys())

        maxId = 0
        for file in os.listdir(self.experimentPath):
            if os.path.basename(file).startswith('clusterJob'):
                currentId = int(file[10:13])
                maxId = max(currentId, maxId)

        clusterJobID = maxId + 1
        #Create clusterJob file containing the trial indices
        clusterJobFile = os.path.join(self.experimentPath, 'clusterJob%03d' % (clusterJobID) + '.yaml')

        clusterJobDict = {'trialIDs' : trialIndices}
        with open(clusterJobFile, 'w') as stream:
            yaml.dump(clusterJobDict , stream)

        self._createSLURMFile(clusterJobID, len(trialIndices), numParallelJobs = numParallelJobs,
                              memory = memory, computationTime = computationTime, accelerator=accelerator)

        cmd = "sbatch " + self.experimentPath + "/jobs.slurm"

        subprocess.check_output(cmd, shell=True)

    def _createSLURMFile(self, clusterJobID, numJobs, numParallelJobs, memory, computationTime, accelerator):

        LSF = '%s/jobs.slurm' % self.experimentPath
        experimentId = 'IAS_%s_%s_%s' % (self.category, self.experimentId, clusterJobID)

        import pypost.experiments
        pathTemplate = os.path.dirname(pypost.experiments.__file__)

        fidIn = open(os.path.join(pathTemplate, 'template.slurm'), 'r')
        fidOut = open(LSF, 'w')

        tline = fidIn.readline()
        numJobsLSF = numJobs

        experimentCode = 'from pypost.experiments import Experiment;'
        experimentCode = experimentCode + 'from %s import %s;' % (self.TrialClass.__module__, self.taskName)
        experimentCode = experimentCode + 'experiment = Experiment(\'%s\',\'%s\', %s, create = False);experiment.load(%d)'%(self.rootDir,self.category, self.taskName, self.experimentId)
        while tline:
            tline = tline.replace('§§experimentName§§', experimentId)
            tline = tline.replace('§§computationTime§§', '%d:%d:00'%(computationTime // 60 ,computationTime % 60))
            tline = tline.replace('§§experimentPath§§', self.experimentPath)
            tline = tline.replace('§§experimentCode§§', experimentCode)
            tline = tline.replace('§§numJobs§§', '%d' % numJobsLSF)
            tline = tline.replace('§§numParallelJobs§§', '%d' % numParallelJobs)
            tline = tline.replace('§§clusterJobID§§', '%d' % clusterJobID)
            tline = tline.replace('§§memory§§', '%d' % memory)
            tline = tline.replace('§§nvidia§§', accelerator)

            fidOut.write(tline)

            tline = fidIn.readline()

        fidIn.close()
        fidOut.close()

    def startJobFromClusterID(self, clusterJobID, jobID):
        clusterJobFile = os.path.join(self.experimentPath, 'clusterJob%03d' % (clusterJobID,) + '.yaml')
        with open(clusterJobFile, 'r') as stream:
            jobDict = yaml.load(stream)

        trialIDs = jobDict['trialIDs']
        trialID = trialIDs[jobID]

        trial = self.loadTrialFromID(trialID)
        trial.start()

    def copy_code_folder(self, src, dst, symlinks=False, ignore=None):
        ign = shutil.ignore_patterns(ignore)
        self.copytree(src, dst, symlinks, ign)

    def copytree(self, src, dst, symlinks=False, ignore=None):
        if not os.path.exists(dst):
            os.makedirs(dst)
            shutil.copystat(src, dst)
        lst = os.listdir(src)
        if ignore:
            excl = ignore(src, lst)
            lst = [x for x in lst if x not in excl]
        for item in lst:
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if symlinks and os.path.islink(s):
                if os.path.lexists(d):
                    os.remove(d)
                os.symlink(os.readlink(s), d)
                try:
                    st = os.lstat(s)
                    mode = stat.S_IMODE(st.st_mode)
                    os.lchmod(d, mode)
                except:
                    pass  # lchmod not available
            elif os.path.isdir(s):
                self.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)


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

    def createTrial(self, evalPath, trialIdx, settings=None):
        '''
        Creates a new trial with given path and index.
        :param evalPath: Path of the evaluation
        :param trialIdx: Trial index
        :return: The newly created trial object
        '''
        return self.TrialClass(evalPath, trialIdx, settings)

    def getNumTrials(self):
        return len(self.trialIndexToDirectorymap)

    def getEvaluationData(self, evaluationCollection):
        if not isinstance(evaluationCollection,list):
            evaluationCollection = [evaluationCollection ]

        evaluationManager = DataManager('evaluations')
        trialManager = DataManager('trials')
        iterationManager = DataManager('iterations')

        evaluationManager.subDataManager = trialManager
        trialManager.subDataManager = iterationManager

        trialTest = self.loadTrialFromID(0)

        propertyList = trialTest.settings.getProperties()
        for prop in propertyList.keys():
            settingsVal = trialTest.settings.getProperty(prop)
            if (isinstance(settingsVal, (list, tuple, np.ndarray))):
                numDim = len(settingsVal)
            else:
                numDim = 1
            evaluationManager.addDataEntry(prop, numDim)

        trialManager.addDataEntry('isFinished', 1)
        trialManager.addDataEntry('isRunning', 1)
        trialManager.addDataEntry('rngState', 1)
        trialManager.addDataEntry('trialID', 1)

        for dataKey in trialTest.data.keys():
            dataVal = trialTest.data[dataKey]

            numIter = 0

            if (isinstance(dataVal, (np.ndarray))):
                numDim = dataVal.shape[1]
                numIter = dataVal.shape[0]
            else:
                numDim = 1

            iterationManager.addDataEntry(dataKey, numDim)

        data = evaluationManager.createDataObject([len(evaluationCollection), 4, 4])

        for i in range(0,len(evaluationCollection)):
            data.reserveStorage(evaluationCollection[i].getNumTrials(), i)

            propertyList = evaluationCollection[i].settings.getProperties()
            for prop in propertyList.keys():
                value = evaluationCollection[i].settings.getProperty(prop)
                if isinstance(value, (bool, int, float, np.ndarray)):
                    data.setDataEntry(prop, i, evaluationCollection[i].settings.getProperty(prop))

            for j in range(0, evaluationCollection[i].getNumTrials()):
                trial = evaluationCollection[i].loadTrialFromID(j)
                numIterations = trial.numIterations

                data[i, j].isFinished = trial.isFinished
                data[i, j].isRunning = trial.isRunning
                data[i, j].rngState = trial.rngState[0]
                data[i, j].trialID = trial.index

                data.reserveStorage(numIterations, [i, j])
                for dataKey in trial.data.keys():
                    data.setDataEntry(dataKey, [i,j], trial.data[dataKey])

        return data
