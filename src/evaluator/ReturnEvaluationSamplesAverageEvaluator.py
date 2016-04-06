'''
Created on Dec 14, 2015

@author: moritz
'''
import numpy as np
from evaluator import Evaluator
from experiments.Trial import StoringType
from common.SettingsClient import SettingsClient

class ReturnEvaluationSamplesAverageEvaluator(Evaluator, SettingsClient):
    '''
    Evaluates the parameterPolicyLearner.KL variable

    Methods (annotated):
    def __init__(self, numSamplesEvaluation: int) -> None
    def getEvaluation(self, data: data.Data, newData: data.Data, trial: experiments.Trial) -> int
    '''

    def __init__(self, numSamplesEvaluation):
        ''' Constructor

        :param numSamplesEvaluation:
        '''
        Evaluator.__init__(self, 'rewardEval', {'preLoop', 'endLoop'}, StoringType.ACCUMULATE)
        SettingsClient.__init__(self)

        self._numSamplesEvaluation = numSamplesEvaluation
        '''
        Number of evaluation samples
        '''

        self._data=None

        self.linkProperty('_numSamplesEvaluation')

    def getEvaluation(self, data, newData, trial):
        if (trial.evaluationSampler) & (not trial.evaluationSampler is None):
            sampler = trial.evaluationSampler
        else:
            sampler = trial.sampler

        dataManager = sampler.getDataManager()

        if self._data is None:
            self.data = dataManager.getDataObject(0);

        numSamplesTmp = sampler.numSamples
        initialSamplesTmp = sampler.numInitialSamples;
        seed = np.random.seed()
        np.random.seed(1000)
        sampler.numSamples = self.numSamplesEvaluation
        sampler.numInitialSamples = self.numSamplesEvaluation
        sampler.createSamples(self._data)
        sampler.numSamples = numSamplesTmp
        sampler.numInitialSamples=initialSamplesTmp
        np.random.seed(seed)

        evaluation = sum(self._data.getDataEntry('returns'))/self._data.getNumElementsForDepth(2)
        self.publish(evaluation)
        self._data = []

        return evaluation
