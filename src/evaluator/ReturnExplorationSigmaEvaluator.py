'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from evaluator import Evaluator
from experiments import StoringType

class ReturnExplorationSigmaEvaluator(Evaluator):
    '''
    Returns the exploration sigma value from all return values
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        super().__init__('explorationSigma', {'endLoop'}, StoringType.ACCUMULATE)
        
    def getEvaluation(self, data, newData, trial):
        # FIXME check if callDataFunctionOutput signature changed
        result=trial.actionPolicy.callDataFunctionOutput('getExpectationAndSigma', data)
        # result now contains [mu, sigma]
        sigma=result[1]
        evaluation=np.mean(sigma)
        
        return evaluation
