from pypost.data import DataManager
import pypost.common.tfutils as tfutils
import tensorflow as tf
import numpy as np
import time
from pypost.mappings.Gaussian import FullGaussian_Base


num_cpu = 1
tf_config = tf.ConfigProto(inter_op_parallelism_threads=num_cpu, intra_op_parallelism_threads=num_cpu)
session = tf.Session(config=tf_config)
session.__enter__()

dataManager = DataManager('data')
dataManager.addDataEntry('states', 10)
dataManager.addDataEntry('actions', 5)

generatorMean = tfutils.continuous_MLP_generator([100, 100])
generatorCovMat = tfutils.constant_covariance_generator()

gaussian = FullGaussian_Base(dataManager, ['states'], ['actions'], generatorMean, generatorCovMat)

data = dataManager.createDataObject([1000])
data[...].states = np.random.normal(0, 1, data[...].states.shape)

A = np.random.normal(0,1,(5,5))
covMat = A.dot(A.transpose())
gaussian.param_covmat = covMat

# Sample from Gaussian and write back in data
data[...] >> gaussian >= data

# compute logLikelihood
data[...] >= gaussian.logLike

# Compute log likelihood
gaussianOther = FullGaussian_Base(dataManager, ['states'], ['actions'], generatorMean, generatorCovMat)

# the param_* properties are created automatically by parsing the mean and logStd tensors. They can be set and read as normal numpy arrays
gaussianOther.params = gaussian.params
# the concatenated parameter vector can be accessed by
gaussianOther.params

# we can also access the tensor variables with
gaussianOther.tv_final_b
# All tensor variables of one object can be found by
gaussianOther.tv_variables_list

tf_klDiv = gaussian.klDivergence(gaussianOther)

klDiff_tf = data[...] >= tf_klDiv

# We can directly view the output of different tensors, i.e., the mean
data[...] >= gaussian.mean

# Or the different layers

data[...] >= gaussian.layers[0]

# We can compute gradients: Tensorflow computes only the sum of the gradients for a loss
start = time.clock()
gradientSum = data[...] >= gaussian.logLike.gradient(gaussian.tv_layer1_w)
print((time.clock() - start)*1000)

# We can compute also the gradients per sample... but thats rather slow
start = time.clock()
gradientSingle = data[...] >= gaussian.logLike.single_gradient(gaussian.tv_layer1_w)
print((time.clock() - start)*1000)

print('Gradient: {0}'.format(gradientSum))
print('GradientSingle: {0}'.format(gradientSingle))

print('GradientDiff: {0}'.format(np.sum(gradientSingle, axis=0) - gradientSum))

