from pypost.data.DataManipulator import DataManipulator
from pypost.common.SettingsClient import SettingsClient
from pypost.common import SettingsManager
from pypost.learner.BatchLearner import BatchLearner
import numpy as np
import scipy.linalg
import math

class NaturalEvolutionStrategy(BatchLearner):
    '''
    properties
        policy;
        shape;
        weights;
        fit;
        rewardName;
        parameterName;
    end

    properties(SetObservable, AbortSet)
        learnRateNESMeans;
        learnRateNESSigmas;
        L;
    end

    methods (Static)
        function [learner] = CreateFromTrial(trial)
            learner = Learner.EpisodicRL.NESLearner2(trial.dataManager, trial.parameterPolicy, 'returns', 'parameters');
        end
    end
    '''

    def __init__(self, dataManager, policy, rewardName='returns', parameterName='parameters'):

        BatchLearner.__init__(self, dataManager)

        self.dataManager = dataManager
        self.policy = policy
        self.rewardName = rewardName
        self.parameterName = parameterName

        minRange = self.dataManager.getMinRange(self.parameterName)
        maxRange = self.dataManager.getMinRange(self.parameterName)

        dimParameters = dataManager.getNumDimensions(parameterName)

        self.L = np.add(4, 3 * np.floor(np.log(dimParameters)))

        self.learnRateNESMeans = 1
        self.learnRateNESSigmas = 0.5 * min(1.0/dimParameters, 0.25)
        #%obj.learnRateNESSigmas = 0.1 ;

        self.linkProperty('learnRateNESMeans')
        self.linkProperty('learnRateNESSigmas')

        self.linkProperty('L', 'numSamplesEpisodes')


        #%obj.settings.setParameter('newSamples', lambda);
        #%obj.settings.setParameter('initialSamples', 0);
        #%obj.settings.setParameter('maxSamples', lambda);

    @DataManipulator.DataMethod(['self.rewardName', 'self.parameterName'], [])
    def updateModel(self, rewards, parameters):
        #print('re', rewards)
        #print('pa', parameters)

        self.shape = np.log(parameters.shape[0] / 2 + 1.0) - np.log(np.arange(1, parameters.shape[0] + 1))
        self.shape[self.shape < 0] = 0
        self.shape = self.shape / np.sum(self.shape)
        self.weights = np.zeros((parameters.shape[0]))
        self.fit = np.zeros((parameters.shape[0]))
        d = self.dataManager.getNumDimensions(self.parameterName)
        expA = self.policy.cholA
        A = scipy.linalg.logm(self.policy.cholA)
        x = self.policy.bias

        if len(parameters.shape) <= 1:
            raise RuntimeError('invalid parameters shape', parameters.shape)

        X = parameters.conj().T

        #print('a', X)
        #print('xL', x, self.L)
        #print('b', np.tile(x, (1,self.L)))
        #print('xL', x, self.L)

        Z = np.linalg.solve(expA, (X-np.tile(x, (1, parameters.shape[0]))))
        #%Z = randn(d,L); X = repmat(x,1,L)+expA*Z;
        if len(rewards.shape) < 2:
            raise RuntimeError('invalid shape', rewards.shape)

        self.fit = -rewards.conj().T
        idx = np.argsort(self.fit)
        self.weights[idx] = self.shape

        if len(self.weights.shape) != 1:
            raise RuntimeError('invalid weights shape', self.weights.shape)

        if len(Z.shape) < 2:
            raise RuntimeError('invalid Z shape', Z.shape)

        #% step 3: compute the gradient for C and x
        G = (np.tile(self.weights, (d, 1)) * Z).dot(Z.conj().T) - sum(self.weights)*np.eye(d)
        # TODO: check this ^

        dx = self.learnRateNESMeans * expA.dot(
            Z.dot(self.weights[np.newaxis, :].T))

        dA = self.learnRateNESSigmas * G

        # The CMA-ES optimizer is a minimizer, we have to take the
        # negative reward function
        x = x + dx
        A = A + dA

        self.policy.setBias(x)
        self.policy.setSigma(scipy.linalg.expm(A))


    def printMessage(obj, data, results, model):
        pass
