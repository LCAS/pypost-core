import numpy as np
from pypost.evaluator import Evaluator
from pypost.experiments.Trial import StoringType


class ReturnSearchDistributionMeanEvaluator(Evaluator):
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
        super().__init__('searchDistributionMean', {'endLoop'}, StoringType.ACCUMULATE)

    def getEvaluation(self, data, newData, trial):
        evaluation=np.matrix([
            np.transpose(trial.parameterPolicy.bias),
            np.transpose(trial.parameterPolicy.weights(...))]);

        return evaluation
