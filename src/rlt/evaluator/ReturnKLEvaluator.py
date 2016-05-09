'''
Created on Dec 14, 2015

@author: moritz
'''
from rlt.evaluator import Evaluator
from rlt.experiments.Trial import StoringType

class ReturnKLEvaluator(Evaluator):
    '''
    Evaluates the parameterPolicyLearner.KL variable

    Methods (annotated):
    def __init__(self) -> None
    def getEvaluation(self, data: data.Data, newData: data.Data, trial: experiments.Trial) -> int
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__('trueKL', {'endLoop'}, StoringType.ACCUMULATE)

    def getEvaluation(self, data, newData, trial):
        evaluation=trial.parameterPolicyLearner.KL
        self.publish(evaluation)

        return evaluation
