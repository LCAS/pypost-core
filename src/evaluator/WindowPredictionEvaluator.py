'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from evaluator import Evaluator
from experiments.Trial import StoringType

class WindowPredictionEvaluator(Evaluator):
    '''
    Returns the max value from all return values
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        super().__init__('windowPrediction', {'endLoop'},
                         StoringType.ACCUMULATE)

        self._numSamplesEvaluation = 100
        '''
        Number of samples to evaluate
        '''
        self._groundtruthName=None
        '''
        Name of the ground truth data
        '''

        self._observationIndex = 0
        '''
        index to observe
        '''

        self._evaluationData=None
        '''
        current evaluation data
        '''

        # FIXME replace magic strings by constants
        # FIXME replace linkProperty
        self.linkProperty('_numSamplesEvaluation','numSamplesEvaluation');
        self.linkProperty('_observationIndex', 'observationIndex');
        self.linkProperty('_groundtruthName','groundtruthName');


    def getEvaluation(self, data, newData, trial):
        raise NotImplementedError()

    def squaredError(data, estimates):
        raise NotImplementedError()

    def euclideanDistances(data, estimates, window_size):
        raise NotImplementedError()
