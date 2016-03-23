'''
Created on Dec 14, 2015

@author: moritz
'''
from evaluator import Evaluator
from experiments.Trial import StoringType
from common.SettingsClient import SettingsClient

class ReturnEvaluationSamplesAverageEvaluator(Evaluator, SettingsClient):
    '''
    Evaluates the parameterPolicyLearner.KL variable
    '''

    def __init__(self, numSamplesEvaluation):
        ''' Constructor

        :param numSamplesEvaluation: 
        '''
        super().__init__('rewardEval', {'preLoop', 'endLoop'}, StoringType.ACCUMULATE)
        
        self._numSamplesEvaluation = numSamplesEvaluation
        '''
        Number of evaluation samples
        '''
        
        self._data=None
        
        self.globalProperties['numSamplesEvaluation'] = numSamplesEvaluation
        self.linkProperty('numSamplesEvaluation')
        
    def getEvaluation(self, data, newData, trial):
        if (trial.evaluationSampler) & (~isempty(trial.evaluationSampler)):
            sampler = trial.evaluationSampler
        else:
            sampler = trial.sampler
        
        dataManager = sampler.getDataManager()
        
        if isempty(self._data):
            self.data = dataManager.getDataObject(0);
        
        numSamplesTmp = sampler.numSamples
        initialSamplesTmp = sampler.numInitialSamples;
        seed = rng
        rng(1000)
        sampler.numSamples = self.numSamplesEvaluation
        sampler.numInitialSamples = self.numSamplesEvaluation
        sampler.createSamples(self._data)
        sampler.numSamples = numSamplesTmp
        sampler.numInitialSamples=initialSamplesTmp
        rng(seed)
        
        evaluation = sum(self._data.getDataEntry('returns'))/self._data.getNumElementsForDepth(2)
        self.publish(evaluation)
        self._data = []

        return evaluation
