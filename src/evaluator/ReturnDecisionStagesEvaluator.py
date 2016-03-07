import numpy as np
from evaluator import Evaluator
from experiments import StoringType


class ReturnDecisionStagesEvaluator(Evaluator):
    '''
    Returns the max value from all return values
    '''

    def __init__(self, sampler, numSamplesEvaluation=100,
                 numStepsEvaluation=50):
        '''
        Constructor

        :param sampler: the sampler to use
        :param numSamplesEvaluation: number of samples to be evaluated,
                                     defaults to 100
        :param numStepsEvaluation: number of steps per samples to be evaluated,
                                   defaults to 50
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
        self.numSamplesEvaluation = numSamplesEvaluation
        '''
        number of samples to be evaluated
        '''
        self.numStepsEvaluation = numStepsEvaluation
        '''
        number of steps per samples to be evaluated
        '''
        self._sampler = sampler

    def getEvaluation(self, data, newData, trial):
        #FIXME setup on _numStepsEvaluation change
        if self.isActiveStepSampler == 0:
            self.isActiveStepSampler = IsActiveNumSteps(trial.dataManager,
                                                        'decisionSteps')
            self.isActiveStepSampler.numTimeSteps = self.numStepsEvaluation

        #FIXME setup on object creation
        if self._sampler.length == 0:
            currSampler = trial.sampler
        else:
            currSampler = self._sampler

        oldSampler = currSampler.stageSampler.isActiveSampler

        currSampler.stageSampler.setIsActiveSampler(self._isActiveStepSampler)

        if (trial.evaluationSampler is not None and
            trial.evaluationSampler.length != 0):
            sampler = trial.evaluationSampler
        else:
            sampler = currSampler

        dataManager = sampler.getDataManager

        if self._data==None:
            self._data = dataManager.getDataObject(0)

            numSamplesTmp = sampler.numSamples
            initialSamplesTmp = sampler.numInitialSamples
            seed = rng
            rng(1000)
            sampler.numSamples = self.numSamplesEvaluation
            sampler.numInitialSamples = self.numSamplesEvaluation
            sampler.createSamples(self._data)

            sampler.numSamples = numSamplesTmp
            sampler.numInitialSamples=initialSamplesTmp
            rng(seed)


            evaluation = mean(obj.data.getDataEntry('rewards'))

            self.publish(evaluation)
            self._data = []

            #FIXME assert?
            assert(evaluation > -5)

            currSampler.stageSampler.setIsActiveSampler(oldSampler)
