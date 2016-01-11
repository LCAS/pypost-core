'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from evaluator import Evaluator
from experiments import StoringType

class ReturnMaxEvaluator(Evaluator):
    '''
    Returns the max value from all return values
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        super().__init__('maxReturn', {'endLoop'}, StoringType.ACCUMULATE)
        
    def getEvaluation(self, data, newData, trial):
        evaluation=np.max(newData.getDataEntry('returns'))
        self.publish(evaluation)
        
        return evaluation
