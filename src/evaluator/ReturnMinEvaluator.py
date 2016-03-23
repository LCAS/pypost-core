'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from evaluator import Evaluator
from experiments.Trial import StoringType

class ReturnMinEvaluator(Evaluator):
    '''
    Returns the min value from all return values
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        super().__init__('minReturn', {'endLoop'}, StoringType.ACCUMULATE)
        
    def getEvaluation(self, data, newData, trial):
        evaluation=np.min(newData.getDataEntry('returns'))
        self.publish(evaluation)
        
        return evaluation
