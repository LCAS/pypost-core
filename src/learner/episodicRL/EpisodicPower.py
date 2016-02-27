import numpy as np

from learner.weightedML.RLByWeightedML import RLByWeightedML


class EpisodicPower(RLByWeightedML, object):
    '''
    Implementation of an episodic PoWER algorithm
    '''

    '''
    FIXME implement this in python
    methods (Static)
        function [learner] = CreateFromTrial(trial)
            learner = Learner.EpisodicRL.EpisodicPower(trial.dataManager, trial.parameterPolicyLearner);
        end

        function [learner] = CreateFromTrialKnowsNoise(trial)
            trial.transitionFunction.registerControlNoiseInData();
            learner = Learner.EpisodicRL.EpisodicPower(trial.dataManager, trial.policyLearner);
            learner.addDataPreprocessor(DataPreprocessors.NoiseActionPreprocessor(trial.dataManager));
            trial.policyLearner.setOutputVariableForLearner('actionsWithNoise');

        end
    '''

    def __init__(self, dataManager, policyLearner):
        '''
        Constructor
        '''

        RLByWeightedML.__init__(dataManager, policyLearner)

        # TODO find default value
        self.divKL = None

        self.temperatureScalingPower = 10.0

        # FIXME where is link property implemented
        self.linkProperty('temperatureScalingPower')

    def computeWeighting(self, rewards):
        maxQ = np.max(rewards)
        minQ = np.min(rewards)

        weighting = np.exp(
            self.temperatureScalingPower * (rewards - maxQ) / ((maxQ - minQ) + 10 ^ -6))
        weighting = weighting / np.sum(weighting)

        self.divKL = self.getKLDivergence(
            np.onces(
                np.size(weighting)),
            weighting)

        return weighting

    def printMessage(self, data):
        # FIXME completely overwrites RLLearner printMessage include this also?
        print("divKL: %f", self.divKL)
