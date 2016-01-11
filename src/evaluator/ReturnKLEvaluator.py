'''
Created on Dec 14, 2015

@author: moritz
'''
from evaluator import Evaluator
from experiments import StoringType

class ReturnKLEvaluator(Evaluator):
    '''
    Evaluates the parameterPolicyLearner.KL variable
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        super().__init__('trueKL', {'endLoop'}, StoringType.ACCUMULATE)
        
    def getEvaluation(self, data, newData, trial):
        evaluation=trial.parameterPolicyLearner.KL
        self.publish(evaluation)
        
        return evaluation
