'''
Created on 22.01.2016

@author: Moritz
'''

import numpy as np

from rlt.learner.episodicRL.EpisodicPower import EpisodicPower


class EpisodicPowerTutorial(object):

    def __init__(self):
        '''
        Constructor
        '''

        self.category = "tutorial"
        self.experiementName = "EpisodicPowerNumSamples"

        self.numTrials = 10
        self.numIterations = 100

        # FIXME replace by gauss function
        self.task = QuadraticBanditTask()

        # FIXME replace by gauss setup
        self.learningSetup = BanditLearningSetup('PowerTemperatureRewardNoise')

        self.evaluator = ReturnEvaluatorEvaluationSamples()
        self.evaluationCriterion = EvaluationCriterion()
        self.evaluationCriterion.registerEvaluator(self.evaluator)

        # FIXME this is not in MatLab code
        self.power = EpisodicPower(dataManager, policyLearner)

        self.standard = Experiments.Evaluation(
            ...,
            {
                'settings.numSamplesEpisodes',
                'settings.numInitialSamplesEpisodes',
                'settings.maxCorrParameters',
                'settings.initSigmaParameters',
                'settings.numSamplesEpisodesVirtual',
                ...,
                'settings.rewardNoiseMult',
                'settings.maxSamples',
                'settings.bayesNoiseSigma',
                'settings.bayesParametersSigma'
            }, {..., 10, 100, 1.0, 0.05, 1000, 0, 100, 1, 10 ^ -3, ...},
            numIterations,
            numTrials)

        self.variablesRewardNoiseMult = Experiments.Evaluation(
            ...,
            {
                'settings.rewardNoise'
            }, {..., 0, ..., 1, ..., 2, ..., 3, ...},
            numIterations,
            numTrials)

        self.variablesTemperatureScalingPower = Experiments.Evaluation(
            ...,
            {
                'settings.temperatureScalingPower'
            }, {..., 25, ..., 5, ..., 10, ..., 15, ..., 20, ...},
            numIterations,
            numTrials)

        self.learner = Experiments.Evaluation(
            ...,
            {
                'learner'
            }, {..., Learner.EpisodicRL.EpisodicPower.CreateFromTrial(), ...},
            numIterations,
            numTrials)

        evaluate = Experiments.Evaluation.getCartesianProductOf([
            standard,
            variablesRewardNoiseMult,
            variablesTemperatureScalingPower,
            learner
        ])

        self.experiment = Experiments.Experiment.createByName(
            self.experimentName,
            self.category,
            ...,
            self.task,
            self.learningSetup,
            self.evaluationCriterion,
            5,
            ...,
            {'127.0.0.1', 2})

        self.experiment.addEvaluation(evalute)
        self.experiment.startLocal()
