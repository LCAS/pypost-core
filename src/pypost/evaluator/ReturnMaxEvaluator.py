'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from pypost.evaluator import Evaluator
from pypost.experiments.Trial import StoringType

class ReturnMaxEvaluator(Evaluator):
    '''
    Returns the max value from all return values

    Methods (annotated):
    def __init__(self) -> None
    def getEvaluation(self, data: data.Data, newData: data.Data, trial: experiments.Trial) -> int
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__('maxReturn', {'endLoop'}, StoringType.ACCUMULATE)

    def getEvaluation(self, data, newData, trial):
        evaluation=np.max(newData.getDataEntry('returns'))
        self.publish(evaluation)

        return evaluation
