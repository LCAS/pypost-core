from learner.RLLearner import RLLearner
from data.DataManipulator import DataManipulator
from common.SettingsClient import SettingsClient
from common import SettingsManager
import numpy as np
import scipy.linalg
import math

class NESLearner2(SettingsClient, DataManipulator, RLLearner):
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

    def __init__(self, dataManager, policy, rewardName='returns',
                    parameterName='parameters'):
        SettingsClient.__init__(self)
        RLLearner.__init__(self)
        DataManipulator.__init__(self, dataManager)

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
        self.linkProperty('L')
        #%obj.fpt
        #%obj.xopt
        SettingsManager.getDefaultSettings().setProperty(
            'newSamplesEpisode', self.L)
        #% Common.Settings().setProperty('initialSamplesEpisode', 0);
        SettingsManager.getDefaultSettings().setProperty('maxSamples', self.L)

        self.registerLearningFunction()

        #%obj.settings.setParameter('newSamples', lambda);
        #%obj.settings.setParameter('initialSamples', 0);
        #%obj.settings.setParameter('maxSamples', lambda);

    def registerLearningFunction(self):
        self.addDataManipulationFunction(self.computePolicyUpdate,
            [self.rewardName, self.parameterName], [])

    def computePolicyUpdate(self, rewards, parameters):
        #print('re', rewards)
        #print('pa', parameters)

        self.shape = max(0.0, np.max(
                         np.log(self.L/2+1.0)-np.log(
                            np.arange(1, self.L + 1))))
        self.shape = self.shape / np.sum(self.shape)
        self.weights = np.zeros((self.L))
        self.fit = np.zeros((self.L))
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

        Z = np.linalg.solve(expA, (X-np.tile(x, (1, self.L))))
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

        self.policy.setBias(x);
        self.policy.setSigma(scipy.linalg.expm(A))

    def updateModel(self, data):
        self.callDataFunction('computePolicyUpdate', data)

    def printMessage(obj, data, results, model):
        pass
