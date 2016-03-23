'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from evaluator import Evaluator
from experiments.Trial import StoringType

class ReturnMeanEvaluator(Evaluator):
    '''
    Returns the average return
    @change: changed class name from NewSampler to Mean to reflect functionality  
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        super().__init__('avgReturn', {'endLoop'}, StoringType.ACCUMULATE)
        
    def getEvaluation(self, data, newData, trial):
        evaluation=np.mean(newData.getDataEntry('returns'))
        self.publish(evaluation)
        
        return evaluation
