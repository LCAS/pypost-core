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
<<<<<<< Updated upstream
        raise NotImplementedError()
=======
        raise NotImplementedError
        #get data
        #TODO
        '''
            if (isempty(self.evaluationData))
                if (isprop(trial,'evaluationSampler') && ~isempty(trial.evaluationSampler))
                    sampler = trial.evaluationSampler;
                else
                    sampler = trial.sampler;
                end
                dataManager = sampler.getDataManager;
                self.evaluationData = dataManager.getDataObject(0);

                numSamplesTmp = sampler.numSamples;
                initialSamplesTmp = sampler.numInitialSamples;
                seed = rng;
                rng(1000);
                sampler.numSamples = self.numSamplesEvaluation;
                sampler.numInitialSamples = self.numSamplesEvaluation;
                sampler.createSamples(self.evaluationData);
                sampler.numSamples = numSamplesTmp;
                sampler.numInitialSamples=initialSamplesTmp;
                rng(seed);

                % preprocess evaluation data
                for i = 1:length(trial.scenario.dataPreprocessorFunctions)
                    self.evaluationData = trial.scenario.dataPreprocessorFunctions{i}.preprocessData(self.evaluationData);
                end
            end

            if not(iscell(trial.evaluationObservations))
                trial.evaluationObservations = {trial.evaluationObservations};
            end
            observations = self.evaluationData.getDataEntry3D(trial.evaluationObservations{1});

            if length(trial.evaluationObservations) == 2 && self.evaluationData.isDataEntry(trial.evaluationObservations{2})
                obsPoints = self.evaluationData.getDataEntry(trial.evaluationObservations{2},1);
            else
                obsPoints = true(1,size(observations,1));
            end
            groundtruth = self.evaluationData.getDataEntry3D(trial.evaluationGroundtruth);
            if not(isempty(trial.evaluationValid))
                valid = logical(self.evaluationData.getDataEntry(trial.evaluationValid,1));
                valid = all(valid,2);
            else
                valid = true(size(observations,2),1);
            end

            observations = observations(:,valid,:);
            groundtruth = groundtruth(:,valid,:);
>>>>>>> Stashed changes

    def squaredError(data, estimates):
        raise NotImplementedError()

    def euclideanDistances(data, estimates, window_size):
        raise NotImplementedError()
