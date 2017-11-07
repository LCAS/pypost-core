import tensorflow as tf
import numpy as np
import pypost.common.tfutils as tfutils
from pypost.data import DataManager
from pypost.mappings import TFMapping
from pypost.mappings import Function_Base


class DiagonalGaussian_Base(Function_Base):

    def __init__(self, dataManager, inputArguments, outputArguments, meanTensorGenerator, logStdTensorGenerator, name = 'DiagGaussian'):

        Function_Base.__init__(self, dataManager, inputArguments, outputArguments, meanTensorGenerator, name = name)

        self.meanTensorGenerator = meanTensorGenerator
        self.logStdTensorGenerator = logStdTensorGenerator

        #self.setTensorsForVariables([self.mean, self.logStd])
        self.setMappingTensorNode(self.sample)

    def clone(self, name):
        clone = DiagonalGaussian_Base(self.dataManager, self.inputVariables, self.outputVariables, self.meanTensorGenerator, self.logStdTensorGenerator, name)
        clone.parameters = self.parameters
        return clone

    def klDivergence(self, other):
        assert isinstance(other, DiagonalGaussian_Base)
        return tfutils.sum(other.logStd - self.logStd + (tf.square(self.std) + tf.square(self.mean - other.mean)) / (2.0 * tf.square(other.std)) - 0.5, axis=-1)

    @TFMapping.TensorMethod()
    def logStd(self):
        logStdTensor = self.logStdTensorGenerator(self.getAllInputTensor(), self.dimOutput)
        return logStdTensor

    @TFMapping.TensorMethod()
    def std(self):
        return tf.exp(self.logStd)

    @TFMapping.TensorMethod()
    def logLike(self):
        entrySample = self.dataManager.createTensorForEntry(self.outputVariables[0])
        return - 0.5 * tfutils.sum(tf.square((entrySample - self.mean) / self.std), axis=-1) \
               - 0.5 * np.log(2.0 * np.pi) * tf.to_float(tf.shape(entrySample)[-1]) \
               - tfutils.sum(self.logStd, axis=-1)

    @TFMapping.TensorMethod()
    def entropy(self):
        return tfutils.sum(self.logStd + .5 * np.log(2.0 * np.pi * np.e), axis=-1)

    @TFMapping.TensorMethod(useAsMapping=True, connectTensorToOutput=True)
    def sample(self):
        return self.mean + self.std * tf.random_normal(tf.shape(self.mean))


class LinearDiagionalGaussian(DiagonalGaussian_Base):
    def __init__(self, dataManager, inputArguments, outputArguments, useBias = True, name = 'Function'):
        DiagonalGaussian_Base.__init__(self, dataManager, inputArguments, outputArguments,
            meanTensorGenerator=tfutils.linear_layer_generator(useBias), logStdTensorGenerator=tfutils.diagional_log_std_generator(), name = name)

class ConstantDiagionalGaussian(DiagonalGaussian_Base):
    def __init__(self, dataManager, inputArguments, outputArguments, useBias = True, name = 'Function'):
        DiagonalGaussian_Base.__init__(self, dataManager, inputArguments, outputArguments,
            meanTensorGenerator=tfutils.constant_generator(), logStdTensorGenerator=tfutils.diagional_log_std_generator(), name = name)



class FullGaussian_Base(Function_Base):

    def __init__(self, dataManager, inputArguments, outputArguments, meanTensorGenerator, covMatrixTensorGenerator, name = 'FullGaussian'):

        Function_Base.__init__(self, dataManager, inputArguments, outputArguments, meanTensorGenerator, name = name)

        self.meanTensorGenerator = meanTensorGenerator
        self.covMatrixTensorGenerator = covMatrixTensorGenerator

        #self.setTensorsForVariables([self.mean, self.covMatrix])
        self.setMappingTensorNode(self.sample)

    def initialize_params(self):
        self.param_covmat = np.eye(self.dimOutput)

    def clone(self, name):
        clone = FullGaussian_Base(self.dataManager, self.inputVariables, self.outputVariables, self.meanTensorGenerator, self.covMatrixTensorGenerator, name)
        clone.parameters = self.parameters
        return clone

    def klDivergence(self, other):
        assert isinstance(other, FullGaussian_Base)

        return tfutils.sum(tf.log(tf.diag_part(other.stdMatrix)) - tf.log(tf.diag_part(self.stdMatrix)) - 0.5) +  0.5 * tf.trace(tf.matrix_solve(other.covMatrix, self.covMatrix)) + \
            0.5 * tfutils.sum(tf.square(tf.matrix_triangular_solve(other.stdMatrix, tf.transpose(other.mean - self.mean))), axis=0)

    @TFMapping.TensorMethod()
    def stdMatrix(self):
        stdMatrixTensor = tf.cholesky(self.covMatrix)
        return stdMatrixTensor

    @TFMapping.TensorMethod()
    def covMatrix(self):
        return self.covMatrixTensorGenerator(self.getAllInputTensor(), self.dimOutput)

    @TFMapping.TensorMethod()
    def logLike(self):
        entrySample = self.dataManager.createTensorForEntry(self.outputVariables[0])
        diffSample = entrySample - self.mean

        return - 0.5 * tfutils.sum(tf.square(tf.matrix_triangular_solve(self.stdMatrix, tf.transpose(diffSample))), axis=0) \
               - 0.5 * np.log(2.0 * np.pi) * self.dimOutput \
               - tfutils.sum(tf.log(tf.diag_part(self.stdMatrix)))

    @TFMapping.TensorMethod()
    def entropy(self):
        return tfutils.sum(tf.log(tf.diag(self.stdMatrix)) + .5 * np.log(2.0 * np.pi * np.e), axis=-1)

    @TFMapping.TensorMethod(useAsMapping=True, connectTensorToOutput=True)
    def sample(self):
        return self.mean + tf.matmul(tf.random_normal(tf.shape(self.mean)), tf.transpose(self.stdMatrix))
