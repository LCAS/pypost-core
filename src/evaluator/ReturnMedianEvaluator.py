'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from evaluator import Evaluator
from experiments import StoringType

class ReturnMedianEvaluator(Evaluator):
    '''
    Returns the median value from all return values
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        super().__init__('medianReturn', {'endLoop'}, StoringType.ACCUMULATE)
        
    def getEvaluation(self, data, newData, trial):
        evaluation=np.median(newData.getDataEntry('returns'))
        self.publish(evaluation)
        
        return evaluation