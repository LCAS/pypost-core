import unittest

import numpy as np

from pypost.data import DataManager
from pypost.mappings.Gaussian import DiagonalGaussian_Base
from pypost.common import tfutils
import tensorflow as tf


class testGaussianLinearInFeatures(unittest.TestCase):

    def testDiagionalGaussian(self):
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


if __name__ == '__main__':
    test = testGaussianLinearInFeatures()
    test.testDiagionalGaussian()

    unittest.main()
