'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from evaluator import Evaluator
from experiments import StoringType

class SupervisedLearningMSEEvaluator(Evaluator):
    '''
    FIXME add description  
    '''

    def __init__(self, additionalName=None):
        '''
        Constructor
        '''
        if additionalName==None:
            additionalName=""
        super().__init__('mseEvaluator'+additionalName, {'endLoop'}, StoringType.ACCUMULATE)
        
    def getEvaluation(self, data, newData, trial):
        evaluationData = self.getEvaluationData(data, trial);
            
        predictedOutput = trial.functionApproximator.callDataFunctionOutput('getExpectationAndSigma', evaluationData);
            
        inputs = evaluationData.getDataEntry(trial.functionApproximator.inputVariables{1});
        outputs = evaluationData.getDataEntry(trial.functionApproximator.outputVariable);
            
        valid = ~any(lambda x: isnan(x),inputs[2]);
        # FIXME check correct translation of ~any(isnan(inputs),2) 
            
        error = predictedOutput[valid,:] - outputs[valid,:]
            
        evaluation = mean(bsxfun(@rdivide, sum(error.^2, 1) / size(error,1), var(outputs)), 2);
        
        return evaluation
    
    def getEvaluationData(self, data, trial):
        '''
        Get the evaluation data from the data & trial objects
        '''
        raise NotImplementedError("Not implemented")
