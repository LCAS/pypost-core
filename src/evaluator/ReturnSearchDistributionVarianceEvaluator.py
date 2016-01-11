'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from evaluator import Evaluator
from experiments import StoringType 

class ReturnSearchDistributionVarianceEvaluator(Evaluator):
    '''
    Evaluates the search distribution variance
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        super().__init__('searchDistributionVariance', {'endLoop'}, StoringType.ACCUMULATE)
        
    def getEvaluation(self, data, newData, trial):
        # FIXME check if callDataFunctionOutput signature changed
        cholAEval = trial.parameterPolicy.cholA;
        
        evaluation = np.transpose(np.diag(cholAEval*np.transpose(cholAEval)))
        
        return evaluation
