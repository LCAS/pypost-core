'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from rlt.evaluator import Evaluator
from rlt.experiments.Trial import StoringType

class ReturnSearchDistributionVarianceEvaluator(Evaluator):
    '''
    Evaluates the search distribution variance

    Methods (annotated):
    def __init__(self) -> None
    def getEvaluation(self, data: data.Data, newData: data.Data, trial: experiments.Trial) -> int
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__('searchDistributionVariance', {'endLoop'}, StoringType.ACCUMULATE)

    def getEvaluation(self, data, newData, trial):
        # FIXME check if callDataFunctionOutput signature changed
        cholAEval = trial.parameterPolicy.cholA;

        evaluation = np.transpose(np.diag(cholAEval*np.transpose(cholAEval)))

        return evaluation
