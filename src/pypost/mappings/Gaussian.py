import tensorflow as tf
import numpy as np
import pypost.common.tfutils as tfutils
from pypost.data import DataManager
from pypost.mappings import TFMapping
from pypost.mappings import Function_Base
from pypost.mappings import LinearFunction
from pypost.mappings import ConstantFunction
from pypost.mappings import MLPFunction



class DiagonalGaussian_Base(TFMapping):

    def __init__(self, dataManager, inputArguments, outputArguments, meanFunction, name = 'DiagGaussian'):

        Function_Base.__init__(self, dataManager, inputArguments, outputArguments, name = name)
        self.meanFunction = meanFunction
        self.additionalScopes.append(meanFunction.name)

    def clone(self, name):
        clone = DiagonalGaussian_Base(self.dataManager, self.inputVariables, self.outputVariables, name)
        clone.params = self.params
        return clone

    def klDivergence(self, other):
        assert isinstance(other, DiagonalGaussian_Base)
        return tfutils.sum(other.tn_logStd - self.tn_logStd + (tf.square(self.tn_std) + tf.square(self.tn_mean - other.tn_mean)) / (2.0 * tf.square(other.tn_std)) - 0.5, axis=-1)

    @TFMapping.TensorMethod()
    def mean(self):
        return self.meanFunction.tn_output

    @TFMapping.TensorMethod()
    def logStd(self):
        assert (False, 'Not implemented in base clase')
        return None

    @TFMapping.TensorMethod()
    def std(self):
        return tf.exp(self.tn_logStd)

    @TFMapping.TensorMethod()
    def logLike(self):
        entrySample = self.dataManager.createTensorForEntry(self.outputVariables[0])
        return - 0.5 * tfutils.sum(tf.square((entrySample - self.tn_mean) / self.tn_std), axis=-1) \
               - 0.5 * np.log(2.0 * np.pi) * tf.to_float(tf.shape(entrySample)[-1]) \
               - tfutils.sum(self.tn_logStd, axis=-1)

    @TFMapping.TensorMethod()
    def entropy(self):
        return tfutils.sum(self.tn_logStd + .5 * np.log(2.0 * np.pi * np.e), axis=-1)

    @TFMapping.TensorMethod(useAsMapping=True, connectTensorToOutput=True)
    def sample(self):
        return self.tn_mean + self.tn_std * tf.random_normal(tf.shape(self.tn_mean))


class LinearDiagonalGaussian(DiagonalGaussian_Base):
    def __init__(self, dataManager, inputArguments, outputArguments, useBias = True, name = 'DiagGaussian'):
        DiagonalGaussian_Base.__init__(self, dataManager, inputArguments, outputArguments, meanFunction = LinearFunction(dataManager, inputArguments, outputArguments, useBias=useBias, name = name), name = name)

    def clone(self, name, inputVariables=None):
        if inputVariables is None:
            inputVariables = self.inputVariables

        clone = LinearDiagonalGaussian(self.dataManager, inputVariables, self.outputVariables, name=name)
        clone.params= self.params
        return clone

    @TFMapping.TensorMethod()
    def logStd(self):
        return tf.get_variable("logstd", shape=[self.dimOutput], initializer=tf.zeros_initializer())


class ConstantDiagonalGaussian(DiagonalGaussian_Base):
    def __init__(self, dataManager, outputArguments, name = 'DiagGaussian'):
        DiagonalGaussian_Base.__init__(self, dataManager, [], outputArguments, meanFunction = ConstantFunction(dataManager, outputArguments, name = name), name = name)

    def clone(self, name, inputVariables=None):

        clone = ConstantDiagonalGaussian(self.dataManager, self.outputVariables, name=name)
        clone.params= self.params
        return clone

    @TFMapping.TensorMethod()
    def logStd(self):
        return tf.get_variable("logstd", shape=[self.dimOutput], initializer=tf.zeros_initializer())


class FullGaussian_Base(TFMapping):

    def __init__(self, dataManager, inputArguments, outputArguments, meanFunction, name = 'FullGaussian'):
        TFMapping.__init__(self, dataManager, inputArguments, outputArguments, name = name)
        self.meanFunction = meanFunction
        self.additionalScopes.append(meanFunction.name)

    def initialize_params(self):
        self.param_stdmat = np.eye(self.dimOutput)

    def clone(self, name):
        clone = FullGaussian_Base(self.dataManager, self.inputVariables, self.outputVariables, name)
        clone.params = self.params
        return clone

    @TFMapping.TensorMethod()
    def mean(self):
        return self.meanFunction.tn_output


    def klDivergence(self, other):
        assert isinstance(other, FullGaussian_Base)

        return tfutils.sum(tf.log(tf.diag_part(other.tn_stdMatrix)) - tf.log(tf.diag_part(self.tn_stdMatrix))) +  0.5 * tf.trace(tf.matrix_solve(other.tn_covMatrix, self.tn_covMatrix)) + \
            0.5 * tfutils.sum(tf.square(tf.matrix_triangular_solve(other.tn_stdMatrix, tf.transpose(other.tn_mean - self.tn_mean))), axis=0) - 0.5 * self.dimOutput

    @TFMapping.TensorMethod()
    def stdMatrix(self):
        assert (False, 'Not implemented in base clase')
        return None

    @TFMapping.TensorMethod()
    def covMatrix(self):
        return tf.matmul(self.tn_stdMatrix, tf.transpose(self.tn_stdMatrix))

    @TFMapping.TensorMethod()
    def logLike(self):
        entrySample = self.dataManager.createTensorForEntry(self.outputVariables[0])
        diffSample = entrySample - self.tn_mean

        return - 0.5 * tfutils.sum(tf.square(tf.matrix_triangular_solve(self.tn_stdMatrix, tf.transpose(diffSample))), axis=0) \
               - 0.5 * np.log(2.0 * np.pi) * self.dimOutput \
               - tfutils.sum(tf.log(tf.diag_part(self.tn_stdMatrix)))

    @TFMapping.TensorMethod()
    def entropy(self):
        return tfutils.sum(tf.log(tf.diag_part(self.tn_stdMatrix)) + .5 * np.log(2.0 * np.pi * np.e), axis=-1)

    @TFMapping.TensorMethod(useAsMapping=True, connectTensorToOutput=True)
    def sample(self):
        return self.tn_mean + tf.matmul(tf.random_normal(tf.shape(self.tn_mean)), tf.transpose(self.tn_stdMatrix))

class LinearFullGaussian(FullGaussian_Base):

    def __init__(self, dataManager, inputArguments, outputArguments, useBias = True, name = 'FullGaussian'):
        FullGaussian_Base.__init__(self, dataManager, inputArguments, outputArguments, meanFunction=LinearFunction(dataManager, inputArguments, outputArguments, useBias = useBias, name = name), name = name)

    @TFMapping.TensorMethod(connectTensorToOutput=True)
    def stdMatrix(self):
        return tf.get_variable("stdmat", shape=[self.dimOutput, self.dimOutput], initializer=tf.ones_initializer())

    def clone(self, name, inputVariables=None):
        if inputVariables is None:
            inputVariables = self.inputVariables

        clone = LinearFullGaussian(self.dataManager, inputVariables, self.outputVariables, name=name)
        clone.params= self.params
        return clone


class FullGaussian(FullGaussian_Base):
    def __init__(self, dataManager, outputArguments, name = 'FullGaussian'):
        FullGaussian_Base.__init__(self, dataManager, [], outputArguments, meanFunction=ConstantFunction(dataManager, outputArguments, name = name), name = name)

    def clone(self, name):
        clone = FullGaussian(self.dataManager, self.outputVariables, name)
        clone.meanFunction = clone.meanFunction.clone(name + 'Mean')
        clone.params = self.params
        return clone

    def clone(self, name):

        clone = FullGaussian(self.dataManager, self.outputVariables, name=name)
        clone.params= self.params
        return clone

    @TFMapping.TensorMethod()
    def stdMatrix(self):
        return tf.get_variable("stdmat", shape=[self.dimOutput, self.dimOutput], initializer=tf.ones_initializer())

    def setMean(self, mu):
        self.param_output = mu.reshape((-1))

    def setCov(self, covMat):
        self.param_stdmat = np.linalg.cholesky(covMat)

class MLPFullGaussian(FullGaussian_Base):
    def __init__(self, dataManager, inputArguments, outputArguments, hiddenLayers, name = 'FullGaussian'):
        FullGaussian_Base.__init__(self, dataManager, inputArguments, outputArguments, meanFunction=MLPFunction(dataManager, inputArguments, outputArguments, hiddenLayers, name = name), name = name)
        self.hiddenLayers = hiddenLayers

    def clone(self, name):
        clone = MLPFullGaussian(self.dataManager,  self.inputVariables, self.outputVariables, self.hiddenLayers, name)
        clone.meanFunction = clone.meanFunction.clone(name + 'Mean')
        clone.params = self.params
        return clone

    @TFMapping.TensorMethod()
    def stdMatrix(self):
        return tf.get_variable("stdmat", shape=[self.dimOutput, self.dimOutput], initializer=tf.ones_initializer())



class NaturalFullGaussian_Base(TFMapping):

    def __init__(self, dataManager, inputArguments, outputArguments, name = 'NaturalFullGaussian'):

        TFMapping.__init__(self, dataManager, inputArguments, outputArguments, name = name)


    def initialize_params(self):
        self.param_precMat = np.eye(self.dimOutput)

    def clone(self, name):
        clone = NaturalFullGaussian_Base(self.dataManager, self.inputVariables, self.outputVariables, name)
        clone.params = self.params
        return clone

    def klDivergence(self, other):
        assert isinstance(other, FullGaussian_Base)

        return tfutils.sum(tf.log(tf.diag_part(other.tn_stdMatrix)) - tf.log(tf.diag_part(self.tn_stdMatrix)) - 0.5) +  0.5 * tf.trace(tf.matrix_solve(other.tn_covMatrix, self.tn_covMatrix)) + \
            0.5 * tfutils.sum(tf.square(tf.matrix_triangular_solve(other.tn_stdMatrix, tf.transpose(other.tn_mean - self.tn_mean))), axis=0)

    @TFMapping.TensorMethod()
    def linearTerm(self):
        assert(False, 'Not implemented in base class')
        return None


    @TFMapping.TensorMethod()
    def precision(self):
        assert (False, 'Not implemented in base class')
        return None

    @TFMapping.TensorMethod()
    def precisionSqrt(self):
        return tf.linalg.cholesky(self.tn_precision)


    @TFMapping.TensorMethod()
    def stdMatrix(self):
        stdMatrixTensor = tf.linalg.cholesky(self.tn_covMatrix)
        return stdMatrixTensor

    @TFMapping.TensorMethod()
    def covMatrix(self):
        return tf.matrix_inverse(self.tn_precision)

    @TFMapping.TensorMethod()
    def mean(self):
        return tf.matmul(self.tn_linearTerm, self.tn_precision)

    @TFMapping.TensorMethod()
    def logLike(self):
        entrySample = self.dataManager.createTensorForEntry(self.outputVariables[0])


        return - 0.5 * tfutils.sum(tf.multiply(tf.transpose(entrySample),tf.matmul(self.tn_precision, tf.transpose(entrySample))), axis=0) \
               - 0.5 * tf.matmul(self.tn_linearTerm, tf.transpose(entrySample)) - 0.5 * tfutils.sum(tf.multiply(self.tn_linearTerm,tf.linalg.solve(self.tn_precision, tf.transpose(self.tn_linearTerm))))\
               - 0.5 * np.log(2.0 * np.pi) * self.dimOutput \
               + tfutils.sum(tf.log(tf.diag_part(self.tn_precisionSqrt)))

    @TFMapping.TensorMethod()
    def entropy(self):
        return tfutils.sum(-tf.log(tf.diag_part(self.tn_precisionSqrt)) + .5 * np.log(2.0 * np.pi * np.e), axis=-1)


    @TFMapping.TensorMethod(useAsMapping=True, connectTensorToOutput=True)
    def sample(self):
        return self.tn_mean + tf.matmul(tf.random_normal(tf.shape(self.tn_mean)), tf.transpose(self.tn_stdMatrix))

class NaturalLinearFullGaussian(NaturalFullGaussian_Base):
    def __init__(self, dataManager, inputArguments, outputArguments, useBias = True, name = 'NaturalGaussian'):
        NaturalFullGaussian_Base.__init__(self, dataManager, inputArguments, outputArguments, name = name)

    @TFMapping.TensorMethod()
    def linearTerm(self):
        return tfutils.create_linear_layer(self.getAllInputTensor(), self.dimOutput, self.useBias)


    @TFMapping.TensorMethod()
    def precision(self):
        quadMat_temp = tf.get_variable('precMat', shape=[self.dimOutput, self.dimOutput], initializer=tf.ones_initializer())

        #enforce symmetric matrix
        quadMat = tf.matrix_band_part(quadMat_temp, -1, 0)
        quadMat = quadMat + tf.transpose(quadMat) - tf.matrix_band_part(quadMat_temp, 0, 0)

        return quadMat


class NaturalFullGaussian(NaturalFullGaussian_Base):
    def __init__(self, dataManager, outputArguments, useBias = True, name = 'Function'):
        NaturalFullGaussian_Base.__init__(self, dataManager, [], outputArguments, name = name)

    @TFMapping.TensorMethod(connectTensorToOutput=True)
    def linearTerm(self):
        empty = self.dataManager.createTensorForEntry('empty')
        empty = tf.matmul(empty, tf.zeros(shape=[0, self.dimOutput]))

        return empty + tf.get_variable('mean', shape=[self.dimOutput], initializer=tf.zeros_initializer())

    @TFMapping.TensorMethod()
    def precision(self):
        quadMat_temp = tf.get_variable('precMat', shape=[self.dimOutput, self.dimOutput],
                                       initializer=tf.ones_initializer())

        # enforce symmetric matrix
        quadMat = tf.matrix_band_part(quadMat_temp, -1, 0)
        quadMat = quadMat + tf.transpose(quadMat) - tf.matrix_band_part(quadMat_temp, 0, 0)

        return quadMat
