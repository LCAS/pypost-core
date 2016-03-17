'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from SupervisedLearningMSEEvaluator import SupervisedLearningMSEEvaluator
from evaluator import Evaluator
from experiments import StoringType

class SupervisedLearningMSETrainEvaluator(SupervisedLearningMSEEvaluator):
    '''
    FIXME add description  
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