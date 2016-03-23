import numpy as np
from evaluator import Evaluator
from experiments.Trial import StoringType


class ReturnSearchDistributionMeanEvaluator(Evaluator):
    '''
    Evaluates the exploration mean value
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        super().__init__('searchDistributionMean', {'endLoop'}, StoringType.ACCUMULATE)

    def getEvaluation(self, data, newData, trial):
        evaluation=np.matrix([
            np.transpose(trial.parameterPolicy.bias),
            np.transpose(trial.parameterPolicy.weights(...))]);

        return evaluation
