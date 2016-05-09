'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from rlt.evaluator.supervisedLearning.SupervisedLearningMSEEvaluator import SupervisedLearningMSEEvaluator
from rlt.evaluator import Evaluator
from rlt.experiments.Trial import StoringType

class SupervisedLearningMSETrainEvaluator(SupervisedLearningMSEEvaluator):
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
        super().__init__('Train')

    def getEvaluationData(self, data, trial):
        '''
        Get the evaluation data from the data & trial objects
        '''
        return data
