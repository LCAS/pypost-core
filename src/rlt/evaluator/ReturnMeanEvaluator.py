'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from rlt.evaluator import Evaluator
from rlt.experiments.Trial import StoringType

class ReturnMeanEvaluator(Evaluator):
    '''
    Returns the average return
    @change: changed class name from NewSampler to Mean to reflect functionality

    Methods (annotated):
    def __init__(self) -> None
    def getEvaluation(self, data: data.Data, newData: data.Data, trial: experiments.Trial) -> int
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__('avgReturn', {'endLoop'}, StoringType.ACCUMULATE)

    def getEvaluation(self, data, newData, trial):
        evaluation=np.mean(newData.getDataEntry('returns'))
        self.publish(evaluation)

        return evaluation
