from pypost.data import DataManager
import pypost.common.tfutils as tfutils
import tensorflow as tf
import numpy as np
from pypost.mappings.Gaussian import DiagonalGaussian_Base


num_cpu = 1
tf_config = tf.ConfigProto(inter_op_parallelism_threads=num_cpu, intra_op_parallelism_threads=num_cpu)
session = tf.Session(config=tf_config)
session.__enter__()

dataManager = DataManager('data')
dataManager.addDataEntry('states', 10)
dataManager.addDataEntry('actions', 5)

generatorMean = tfutils.continuous_MLP_generator([100, 100])
generatorLogStd = tfutils.diagional_log_std_generator()

gaussian = DiagonalGaussian_Base(dataManager, ['states'], ['actions'], generatorMean, generatorLogStd)

data = dataManager.createDataObject([10])
data[...].states = np.random.normal(0, 1, data[...].states.shape)

# Sample from Gaussian and write back in data
data[...] >> gaussian >= data

# compute logLikelihood
data[...] >= gaussian.logLike

# Compute log likelihood
gaussianOther = DiagonalGaussian_Base(dataManager, ['states'], ['actions'], generatorMean, generatorLogStd)

# the param_* properties are created automatically by parsing the mean and logStd tensors. They can be set and read as normal numpy arrays
gaussianOther.param_final_b = np.random.normal(0, 1, (5,))
gaussianOther.param_logstd = np.random.normal(0, 1, (5,))

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





