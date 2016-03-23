'''
Created on Dec 14, 2015

@author: moritz
'''
from numpy.linalg.linalg import eig
from evaluator import Evaluator
from experiments.Trial import StoringType
from evaluator import LogType

class RMatrixEvaluator(Evaluator):
    '''
    Evaluates if every eigenvalue is positive

    Methods (annotated):
    def __init__(self, params) -> 
    getEvaluation(self, data, newData, trial)
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        super().__init__('RMatrix', {'endLoop'}, StoringType.ACCUMULATE)
        
    def getEvaluation(self, data, newData, trial):
        '''
        Evaluates to 0 if every eigenvalue is less-than 0
        and to 1 otherwise
        '''
        #FIXME hard coded access path: learner.Raa. Define interface ...
        r = trial.learner.Raa
        
        #FIXME check for correct eig function
        if all(map(lambda x: x<0,eig(r))):
            evaluation = 0
        else:
            evaluation = 1
            self.publish("Warning: The R matrix is not negative definite",LogType.WARNING)
        
        return evaluation
        