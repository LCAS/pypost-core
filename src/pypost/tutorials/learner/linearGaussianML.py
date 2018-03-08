from pypost.data import DataManager
import pypost.common.tfutils as tfutils
import tensorflow as tf
import numpy as np
import time
from pypost.learner import LinearGaussianMLLearner
from pypost.learner.InputOutputLearner import LogLikeGradientLearner
from pypost.learner.InputOutputLearner import L2GradientLearner
from pypost.common import getDefaultSettings
from pypost.optimizer import TFOptimizerType

from pypost.mappings.Gaussian import LinearFullGaussian



num_cpu = 1
tf_config = tf.ConfigProto(inter_op_parallelism_threads=num_cpu, intra_op_parallelism_threads=num_cpu)
session = tf.Session(config=tf_config)
session.__enter__()

dataManager = DataManager('data')
dataManager.addDataEntry('states', 4)
dataManager.addDataEntry('actions', 6)

settings = getDefaultSettings()

gaussian = LinearFullGaussian(dataManager, ['states'], ['actions'])

data = dataManager.createDataObject([10000])
data[...].states = np.random.normal(0, 1, data[...].states.shape)

A = np.random.normal(0,1,(dataManager.getNumDimensions('actions'),dataManager.getNumDimensions('actions')))
covMat = A.dot(A.transpose())
gaussian.param_stdmat = np.linalg.cholesky(covMat)
gaussian.param_final_w = np.random.normal(0, 1, gaussian.param_final_w.shape)
gaussian.param_final_b = np.random.normal(0, 1, gaussian.param_final_b.shape)


# Sample from Gaussian and write back in data
data[...] >> gaussian >> data

# Compute log likelihood
gaussianLearned = LinearFullGaussian(dataManager, ['states'], ['actions'])
learner = LinearGaussianMLLearner(dataManager, gaussianLearned)

data[...] >> learner

print('LogLike: ', np.sum(data[...] >= gaussianLearned.logLike))

print('Bias1: {0}'.format(gaussian.param_final_b))
print('Bias2: {0}'.format(gaussianLearned.param_final_b))

print('Weights1: {0}'.format(gaussian.param_final_w))
print('Weights2: {0}'.format(gaussianLearned.param_final_w))

print('CovMat1: {0}'.format(gaussian.param_stdmat))
print('CovMat2: {0}'.format(gaussianLearned.param_stdmat))

gradient = data[...] >= gaussian.logLike.gradient()
print(gradient)

settings.setProperty('tfOptimizerType', TFOptimizerType.Adam)
settings.setProperty('tfOptimizerNumIterations', 10000)

gaussianLearned2 = LinearFullGaussian(dataManager, ['states'], ['actions'])
gradientLearner = LogLikeGradientLearner(dataManager, gaussianLearned2)
data[...] >> gradientLearner
