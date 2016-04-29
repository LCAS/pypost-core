'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from rlt.evaluator import Evaluator
from experiments.Trial import StoringType

class SupervisedLearningMSEEvaluator(Evaluator):
    '''
    FIXME add description

    Methods (annotated):
    def __init__(self, additionalName: str ='') -> None
    def getEvaluation(self, data: data.Data, newData: data.Data, trial: experiments.Trial) -> None
    '''

    def __init__(self, additionalName=''):
        '''
        Constructor
        '''
        super().__init__('mseEvaluator'+additionalName, {'endLoop'},
                         StoringType.ACCUMULATE)

    def getEvaluation(self, data, newData, trial):
        evaluationData = self.getEvaluationData(data, trial)

        predictedOutput = trial.functionApproximator.callDataFunctionOutput(
            'getExpectationAndSigma', evaluationData)

        inputs = evaluationData.getDataEntry(
            trial.functionApproximator.inputVariables[1])
        outputs = evaluationData.getDataEntry(
            trial.functionApproximator.outputVariables[0])

        raise NotImplementedError()
        # TODO: not implemented

    def getEvaluationData(self, data, trial):
        '''
        Get the evaluation data from the data & trial objects
        '''
        raise NotImplementedError("Not implemented")
