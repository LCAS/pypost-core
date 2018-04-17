from pypost.data import DataManager
import pypost.common.tfutils as tfutils
import tensorflow as tf
import numpy as np
import time
from pypost.mappings.Gaussian import FullGaussian
from pypost.mappings.Gaussian import NaturalFullGaussian



num_cpu = 1
tf_config = tf.ConfigProto(inter_op_parallelism_threads=num_cpu, intra_op_parallelism_threads=num_cpu)
session = tf.Session(config=tf_config)
session.__enter__()

dataManager = DataManager('data')
dataManager.addDataEntry('states', 10)
dataManager.addDataEntry('actions', 5)

gaussian = FullGaussian(dataManager, ['actions'])
naturalGaussian = NaturalFullGaussian(dataManager, ['actions'])

data = dataManager.createDataObject([100])
data[...].states = np.random.normal(0, 1, data[...].states.shape)

A = np.random.normal(0,1,(5,5))
covMat = A.dot(A.transpose())
gaussian.param_stdmat = np.linalg.cholesky(covMat)
naturalGaussian.param_precMat = np.linalg.inv(covMat)
naturalGaussian.param_linearTerm = naturalGaussian.param_precMat.dot(gaussian.param_output)

data[1,2].empty

# Sample from Gaussian and write back in data
data[...] >> gaussian >= data

# compute logLikelihood
data[1] >= gaussian.logLike

# compute logLikelihood
grad1 = data[...] >= gaussian.tn_logLike.single_gradient()
grad2 = data[...] >= naturalGaussian.tn_logLike.single_gradient()

print('Hello')