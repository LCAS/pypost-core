'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from evaluator import Evaluator
from experiments import StoringType

class ReturnDecisionStagesEvaluator(Evaluator):
    '''
    Returns the max value from all return values
    '''

    def __init__(self, numSamplesEvaluation=None, numStepsEvaluation=None, sampler=None):
        '''
        Constructor
        '''
        super().__init__('rewardEval', {'endLoop'}, StoringType.ACCUMULATE)
        
        self._data=None
        '''
        current data to be evaluated
        '''
        self._isActiveStepSampler = []
        '''
        all isActiveStepSampler which are currently active
        '''
        self._sampler = []
        '''
        all sampler instances to be evaluated
        '''
        if numSamplesEvaluation==None:
            numSamplesEvaluation=100
        numSamplesEvaluation = numSamplesEvaluation
        '''
        number of samples to be evaluated
        '''
        if numStepsEvaluation==None:
            numStepsEvaluation=50
        numStepsEvaluation = numStepsEvaluation
        '''
        number of steps per samples to be evaluated
        FIXME sampler should be required
        '''
        if ~(sampler==None):
            self._sampler = sampler
        
    def getEvaluation(self, data, newData, trial):
        #FIXME setup on _numStepsEvaluation change
        if self._isActiveStepSampler.length==0:
            self._isActiveStepSampler = IsActiveNumSteps(trial.dataManager, 'decisionSteps');
            self._isActiveStepSampler.numTimeSteps = self._numStepsEvaluation;
            
        #FIXME setup on object creation
        if self._sampler.length==0:
            currSampler = trial.sampler
        else:
            currSampler = self._sampler
        
        oldSampler = currSampler.stageSampler.isActiveSampler;
        
        currSampler.stageSampler.setIsActiveSampler(self._isActiveStepSampler);
        
        if (~(trial.evaluationSampler==None) && (~(trial.evaluationSampler.length==0)):
            sampler = trial.evaluationSampler
        else:
            sampler = currSampler
        end
        dataManager = sampler.getDataManager
            
        if self._data==None:
            self._data = dataManager.getDataObject(0);
        end
            
            
            
            numSamplesTmp = sampler.numSamples;
            initialSamplesTmp = sampler.numInitialSamples;
            seed = rng;
            rng(1000);
            sampler.numSamples = obj.numSamplesEvaluation;
            sampler.numInitialSamples = obj.numSamplesEvaluation;
            sampler.createSamples(obj.data);
            
            sampler.numSamples = numSamplesTmp;
            sampler.numInitialSamples=initialSamplesTmp;
            rng(seed);

            
            evaluation = mean(obj.data.getDataEntry('rewards'));
            
            self.publish(evaluation)
            self._data = [];
            
            #FIXME assert?
            assert(evaluation > -5);
            
            currSampler.stageSampler.setIsActiveSampler(oldSampler);
        end
        
   
        
        
    end
    
end