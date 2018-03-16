from pypost.data import DataManager
import pypost.common.tfutils as tfutils
import tensorflow as tf
import numpy as np
import time
from pypost.learner.InputOutputLearner import CrossEntropyLossGradientLearner
from pypost.common import getDefaultSettings
from pypost.optimizer import TFOptimizerType

from pypost.mappings.Classifier import LinearClassifier



num_cpu = 1
tf_config = tf.ConfigProto(inter_op_parallelism_threads=num_cpu, intra_op_parallelism_threads=num_cpu)
session = tf.Session(config=tf_config)
session.__enter__()

dataManager = DataManager('data')
dataManager.addDataEntry('states', 2)
dataManager.addDataEntry('labels', 1)

settings = getDefaultSettings()

settings.setProperty('tfOptimizerType', TFOptimizerType.Adam)
settings.setProperty('tfOptimizerNumIterations', 10000)

classifier = LinearClassifier(dataManager, ['states'], ['labels'])
learner = CrossEntropyLossGradientLearner(dataManager, classifier)

data = dataManager.createDataObject([200])

mean1 = np.array([1, 2])
var1 = np.array([[1,0],[0,1]])

mean2 = np.array([10, 8])
var2 = np.array([[2,0],[0,2]])


data[slice(0,100)].states = np.random.multivariate_normal(mean1, var1, 100)
data[slice(0,100)].labels = np.zeros((100,))

data[slice(100,200)].states = np.random.multivariate_normal(mean2, var2, 100)
data[slice(100,200)].labels = np.ones((100,))

data[...] >> learner

prediction = data[...] >= classifier
