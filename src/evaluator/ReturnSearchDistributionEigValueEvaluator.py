'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from numpy.linalg.linalg import eig
from evaluator import Evaluator
from experiments.Trial import StoringType

class ReturnSearchDistributionEigValueEvaluator(Evaluator):
    '''
    Evaluates the exploration mean value
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        super().__init__('searchDistributionEigValue', {'endLoop'}, StoringType.ACCUMULATE)
        
    def getEvaluation(self, data, newData, trial):
        cholAEval = trial.parameterPolicy.cholA;
        
        evaluation = np.transpose(eig(np.transpose(cholAEval)*cholAEval))
        
        return evaluation
