'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from SupervisedLearningMSEEvaluator import SupervisedLearningMSEEvaluator
from evaluator import Evaluator
from experiments.Trial import StoringType

class SupervisedLearningMSETestEvaluator(SupervisedLearningMSEEvaluator):
    '''
    FIXME add description
    '''

    def __init__(self, additionalName=None):
        '''
        Constructor
        '''
        super().__init__('Test')

        self._numSamplesEvaluation = 100
        '''
        Number of samples to evaluate
        '''

        self._evaluationData=None
        '''
        Evaluation data
        '''

    def getEvaluationData(self, data, trial):
        '''
        Get the evaluation data from the data & trial objects
        '''
        sampler = Sampler.SamplerFromFile(trial.dataManager, trial.fileNameTest)
        #FIXME wait for concept for in/output

        dataManager = sampler.getDataManager
        self._evaluationData = dataManager.getDataObject(0)

        seed = rng()
        sampler.numImitationEpisodes = self._numSamplesEvaluation
        sampler.createSamples(self._evaluationData)
        rng(seed)

        # preprocess evaluation data
        for i in range(0, length(trial.scenario.dataPreprocessorFunctions)):
            self.evaluationData = trial.scenario.dataPreprocessorFunctions[i].\
                preprocessData(self._evaluationData)

        data = self._evaluationData

        return data
