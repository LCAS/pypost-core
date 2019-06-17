import tensorflow as tf
import pypost.common.tfutils as tfutils
from pypost.mappings import TFMapping, Mapping
from pypost.data import DataManager
import numpy as np


class Function_Base(TFMapping):
    def __init__(self, dataManager, inputArguments, outputArguments, name = 'Function'):
        TFMapping.__init__(self, dataManager, inputArguments, outputArguments, name = name)

    def clone(self, name):
        clone = Function_Base(self.dataManager, self.inputVariables, self.outputVariables, name)
        clone.params = self.params
        return clone

    @TFMapping.TensorMethod(connectTensorToOutput=True, useAsMapping=True)
    def output(self):
        raise NotImplementedError()


class LinearParameterInterface():

    def setLinearParameters(self, parameterMatrix):
        return

    def getLinearParameters(self):
        return

    def getLinearFeatures(self, input):
        return


class ConstantFunction(Function_Base, LinearParameterInterface):

    def __init__(self, dataManager, outputArguments, name = 'Function'):
        Function_Base.__init__(self, dataManager, [], outputArguments, name = name)

    def clone(self, name):

        clone = ConstantFunction(self.dataManager, self.outputVariables,  name)
        clone.params = self.params
        return clone

    def setLinearParameters(self, parameterMatrix):
        self.params_output = parameterMatrix

    def getLinearParameters(self):
        return self.params_output

    def getLinearFeatures(self, input):
        return np.ones((input.shape[0],1))

    @TFMapping.TensorMethod(connectTensorToOutput=True, useAsMapping=True)
    def output(self):
        empty = self.dataManager.createTensorForEntry('empty')
        empty = tf.matmul(empty, tf.zeros(shape=[0, self.dimOutput]))

        return empty + tf.get_variable('output', shape=[self.dimOutput], initializer=tf.zeros_initializer())


class LinearFunction(Function_Base, LinearParameterInterface):

    def __init__(self, dataManager, inputArguments, outputArguments, useBias=True, name='Function'):
        Function_Base.__init__(self, dataManager, inputArguments, outputArguments, name=name)
        self.useBias = useBias

    def clone(self, name):

        clone = LinearFunction(self.dataManager, self.inputVariables, self.outputVariables,  useBias=self.useBias, name = name)
        clone.params = self.params
        return clone

    def setLinearParameters(self, parameterMatrix):
        self.param_final_w = parameterMatrix[:, 1:].transpose()
        self.param_final_b = parameterMatrix[:,0].squeeze()

    def getLinearParameters(self):
        return np.hstack((self.param_final_b.reshape((self.param_final_b[0],1)),self.param_final_w)).transpose()

    def getLinearFeatures(self, input):
        if self.useBias:
            return np.hstack((np.ones((input.shape[0], 1)), input))
        else:
            return input

    @TFMapping.TensorMethod(connectTensorToOutput=True, useAsMapping=True)
    def output(self):
        return tfutils.create_linear_layer(self.getAllInputTensor(), self.dimOutput, self.useBias)


class MLPFunction(Function_Base):

    def __init__(self, dataManager, inputArguments, outputArguments, hiddenNodes, name = 'Function'):
        Function_Base.__init__(self, dataManager, inputArguments, outputArguments, name = name)
        self.hiddenNodes = hiddenNodes
        self._setLayersFromTensor(self.tn_output)

    def clone(self, name):

        clone = MLPFunction(self.dataManager, self.inputVariables, self.outputVariables,
                            hiddenNodes=self.hiddenNodes, name=name)
        clone.params = self.params
        return clone

    @TFMapping.TensorMethod(connectTensorToOutput=True, useAsMapping=True)
    def output(self):
        return tfutils.create_layers_linear_ouput(self.getAllInputTensor(), self.hiddenNodes, self.dimOutput)


class QuadraticFunction_Base(Function_Base):

    def __init__(self, dataManager, inputArguments, outputArguments, name = 'QuadraticFunction'):

        TFMapping.__init__(self, dataManager, inputArguments, outputArguments, name = name)

    @TFMapping.TensorMethod()
    def quadraticTerm(self):
        raise NotImplementedError()

    @TFMapping.TensorMethod()
    def linearTerm(self):
        raise NotImplementedError()

    @TFMapping.TensorMethod()
    def constantTerm(self):
        raise NotImplementedError()

    @TFMapping.TensorMethod(connectTensorToOutput=True, useAsMapping=True)
    def output(self):
        entrySample = self.getAllInputTensor()

        meanTensor = tfutils.sum(tf.multiply(tf.transpose(entrySample),
                                             tf.matmul(self.tn_quadraticTerm, tf.transpose(entrySample))), axis=0) \
                     + tf.matmul(tf.transpose(self.tn_linearTerm), tf.transpose(entrySample)) + self.tn_constantTerm
        return meanTensor


class QuadraticFeatureExpansion(Mapping):

    def __init__(self, dataManager, inputArguments, outputName=None):
        if outputName is None:
            outputName = inputArguments[0] + 'SquaredFeatures'
        dim = dataManager.getNumDimensions(inputArguments[0])
        dim = 1 + dim + dim * (dim + 1) / 2
        dataManager.addDataEntry(outputName, int(dim))

        super().__init__(dataManager, inputArguments, outputName)

        dataManager.addFeatureMapping(self)
        self.setLazyEvaluation(False)

    @Mapping.MappingMethod()
    def squaredFeatures(self, input):
        return np.array([[x1 * x2 for i, x1 in enumerate(x) for x2 in x[i:]] + list(x) + [1] for x in input])


class QuadraticFunction(QuadraticFunction_Base, LinearParameterInterface):
    def __init__(self, dataManager, inputArguments, outputArguments, name='QuadraticFunctionConstCoeff'):
        QuadraticFunction_Base.__init__(self, dataManager, inputArguments, outputArguments, name=name)
        self.indicesRow = []
        self.indicesColumn = []
        self.multiplier = []

        for i in range(self.dimInput):
            self.multiplier = self.multiplier + [1] + [2] * (self.dimInput - i - 1)
            self.indicesRow = self.indicesRow + [i] * (self.dimInput - i)
            self.indicesColumn = self.indicesColumn + list(range(i,self.dimInput))
        self.multiplier = np.array(self.multiplier)

    def setLinearParameters(self, parameterMatrix):
        #this only works for 1-D output
        theta = parameterMatrix[0,:]
        r = theta[-self.dimInput - 1:-1]
        R = np.zeros([self.dimInput, self.dimInput])
        R[self.indicesRow, self.indicesColumn] = theta[:-self.dimInput - 1]
        R = (R + R.transpose()) / 2
        r0 = theta[-1]

        self.param_quadTerm = R
        self.param_linearTerm = r.reshape((-1,1))
        self.param_constTerm = r0

    def getLinearParameters(self):
        return np.hstack((self.multiplier * self.param_quadTerm[self.indicesRow, self.indicesColumn],self.param_linearTerm[:,0], self.param_constTerm))

    def getLinearFeatures(self, input):
        return np.array([[x1 * x2 for i, x1 in enumerate(x) for x2 in x[i:]] + list(x) + [1] for x in input])

    @TFMapping.TensorMethod()
    def quadraticTerm(self):
        quadMat_temp = tf.get_variable('quadTerm', shape=[self.dimInput, self.dimInput], initializer=tf.ones_initializer())
        quadMat = tf.matrix_band_part(quadMat_temp, -1, 0)
        quadMat = quadMat + tf.transpose(quadMat) - tf.matrix_band_part(quadMat_temp, 0, 0)
        return quadMat

    @TFMapping.TensorMethod()
    def linearTerm(self):
        return tf.get_variable('linearTerm', shape=[self.dimInput,1], initializer=tf.zeros_initializer())

    @TFMapping.TensorMethod()
    def constantTerm(self):
        return tf.get_variable('constTerm', shape=[1], initializer=tf.zeros_initializer())


if __name__ == "__main__":
    num_cpu = 1
    tf_config = tf.ConfigProto(inter_op_parallelism_threads=num_cpu, intra_op_parallelism_threads=num_cpu)
    session = tf.Session(config=tf_config)
    session.__enter__()


    dataManager = DataManager('data')
    dataManager.addDataEntry('states', 10)
    dataManager.addDataEntry('actions', 5)
    dataManager.addDataEntry('rewards', 1)

    function = LinearFunction(dataManager, ['states'], ['actions'])

    quadraticFeatures = QuadraticFeatureExpansion(dataManager, ['actions'])

    data = dataManager.createDataObject([10])
    data[...].states = np.random.normal(0, 1, data[...].states.shape)

    quadraticFunction = QuadraticFunction(dataManager, ['actions'], ['rewards'])


    print('Hello')


