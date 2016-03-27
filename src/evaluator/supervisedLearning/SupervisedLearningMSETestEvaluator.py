'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from evaluator.supervisedLearning.SupervisedLearningMSEEvaluator import SupervisedLearningMSEEvaluator
from evaluator import Evaluator
from experiments.Trial import StoringType
import sampler

class SupervisedLearningMSETestEvaluator(SupervisedLearningMSEEvaluator):
    '''
    FIXME add description

    Methods (annotated):
    def __init__(self, additionalName: str =None) -> None
    def getEvaluationData(self, data: data.Data, trial: experiments.Trial) -> data.Data
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
        sampler = SamplerFromFile(trial.dataManager, trial.fileNameTest)
        #FIXME wait for concept for in/output

        dataManager = sampler.getDataManager
        self._evaluationData = dataManager.getDataObject(0)

        seed = np.random.seed()
        sampler.numImitationEpisodes = self._numSamplesEvaluation
        sampler.createSamples(self._evaluationData)
        np.random.seed(seed)

        # preprocess evaluation data
        for i in range(0, len(trial.scenario.dataPreprocessorFunctions)):
            self.evaluationData = trial.scenario.dataPreprocessorFunctions[i].\
                preprocessData(self._evaluationData)

        data = self._evaluationData

        return data
