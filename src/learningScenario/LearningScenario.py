from learningScenario.MaxSamplesDeletionStrategy import MaxSamplesDeletionStrategy
from dataProprocessor.DataPreprocessor import DataPreprocessor
from sampler import SamplerPool
from data.DataCollection import DataCollection
import time

class LearningScenario(object):
    '''
    classdocs
    '''


    def __init__(self, dataManager, evalCriterion, sampler):
        '''Creates a new LearningScenario.
        '''

        self.newDataObjects = None
        self.deletionStrategies = []
        self.learners = []
        self.initialLearners = []
        self.initialSamplers = []
        self.initialDataPreprocessors = []
        self.dataPreprocessorFunctions = []
        self.initObjects = []
        self.evalCriterion = evalCriterion
        self.samplers = []
        self.samplers.append(sampler)
        self.dataManager = dataManager

        self.addDeletionStrategy(MaxSamplesDeletionStrategy())

    def addInitObject(self, initObject):
        if initObject is not None:
            self.initObjects.append(initObject)

    def addDataPreprocessor(self, dataPreprocessor, addBeginning = False):
        if addBeginning:
            self.dataPreprocessorFunctions.insert(0, dataPreprocessor)
        else:
            self.dataPreprocessorFunctions.append(dataPreprocessor)

    def addDataPreprocessorBeforePreprocessor(self, DataPreprocessor, preProcessorBefore):
        try:
            index = self.dataPreprocessorFunctions.index(preProcessorBefore)
            self.dataPreprocessorFunctions.insert(index, object)
        except ValueError:
            print('DataPreProcessor for adding new DataPreprocessor not found') 
            raise

    def addInitialDataPreprocessor(self, dataPreprocessor):
        self.initialDataPreprocessors.append(dataPreprocessor)

    def initAllObjects(self):
        self.dataManager.finalizeDataManager()
        self.newDataObjects = self.dataManager.getDataObject(0)
        

        for i in self.initObjects:
            i.initObject()

    def getNewDataObject(self, index):
        return self.newDataObjects(index)

    def createSamples(self, data, iteration):
        if iteration > 0:
            for i in range(0,len(self.samplers)):
                self.samplers[i].setSamplerIteration(iteration)
                #ASK: %obj.newDataObjects(i).resetFeatureTags()
                self.samplers[i].createSamples(self.newDataObjects[i])

                if self.samplers[i].appendNewSamples():
                    data.mergeData(self.newDataObjects[i])#ToDo
                    #newSampleIndices = #TODO
                else:
                    data.mergeData(self.newDataObjects[i])
                    #newSamplerIndices = #TODO

                for l in self.learners:
                    l.addedData(data, newSampleIndices)
        else:
            for i in range()

    def addSampler(self, sampler):
        self.samplers.append(sampler)

    def addInitialSampler(self, sampler):
        self.initialSamplers.append(sampler)

    def addLearner(self, learner):
        self.learners.append(learner)

    def addInitialLearner(self, learner):
        self.learners.append(learner)
        self.addInitialDataPreprocessor(learner)

    def addDeletionStrategy(self, deletionStrategy):
        self.deletionStrategies.append(deletionStrategy)

    def deleteSamples(self, data, beforeLearning):
        for d in self.deletionStrategies:
            if beforeLearning:
                keepIndices = d.getIndicesToKeepBeforeLearning(data)
            else:
                keepIndices = d.getIndicesToKeepAfterLearning(data)
            if keepIndices is not None:
                for l in self.learners:
                    l.deletedData(data, keepIndices)
                data.deleteData(keepIndices)

    def learnScenario(self, trial):
        if trial.iterIdx == 1:
            rng(trial.rngState)
            self.initAllObjects()
            data = self.dataManager.getDataObject(0)

            self.createSamples(data, 0)

            for i in self.initialDataPreprocessors:
                i.setIteration(0)

                #ASK: if?
                data = i.preprocessData(data)

            for i in self.initialLearners:
                i.updateModel(data)

            if trial.resetInitialData:
                data = self.dataManager.getDataObject(0)
        else:
            data = self.dataManager.getDataObject(0)
            data.copyValuesFromDataStructure(trial.data)

        #At the start??
        if trial.iterIdx == 1:
            rng(trial.rngState)
            self.evalCriterion.evaluate(trial, 'preLoop')

        dataCollection = DataCollection(data)
        tStartTrial = time.time()

        while not trial.isFinished():
            self.evalCriterion.evaluate(trial, 'startLoop')

            tStartLearnScenario = time.time()

            self.createSamples(data, trial.iterIdx)

            tGetRealData = time.time() - tStartLearnScenario
            print("Sampling real data took:", tGetRealData, "seconds")

            self.deleteSamples(data, True)

            # Preprocess data
            for d in self.dataPreprocessorFunctions:
                d.setIteration(trial.iterIdx)
                d.preprocessDataCollection(dataCollection)

            self.evalCriterion.evaluate(trial, 'afterPreproc')

            # Update all learners
            for l in self.learners:
                l.setIteration(trial.iterIdx)
                l.updateModelCollection(dataCollection)

            tLearnScenario = time.time() - tStartLearnScenario
            print("Learning the Scenario took:", tLearnScenario, "seconds")

            tTrialTmp = tStartTrial - time.time()
            print("So far the trial took:", tTrialTmp, "seconds")

            self.evalCriterion.evaluate(trial, 'endLoop')

            self.printMessage(trial, data)

            trial.store('rngState', rng())
            self.evalCriterion.nextIteration(trial, data)

            self.deleteSamples(data, False)
        self.evalCriterion.evaluate(trial, 'postLoop')