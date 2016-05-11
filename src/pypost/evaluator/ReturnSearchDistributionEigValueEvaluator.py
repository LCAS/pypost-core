'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from numpy.linalg.linalg import eig
from pypost.evaluator import Evaluator
from pypost.experiments.Trial import StoringType

class ReturnSearchDistributionEigValueEvaluator(Evaluator):
    '''
    Evaluates the exploration mean value

    Methods (annotated):
    def __init__(self) -> None
    def getEvaluation(self, data: data.Data, newData: data.Data, trial: experiments.Trial) -> int
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__('searchDistributionEigValue', {'endLoop'}, StoringType.ACCUMULATE)

    def getEvaluation(self, data, newData, trial):
        cholAEval = trial.parameterPolicy.cholA;

        evaluation = np.transpose(eig(np.transpose(cholAEval)*cholAEval))

        return evaluation
