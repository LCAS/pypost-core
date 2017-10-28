import tensorflow as tf
import pypost.common.tfutils as tfutils
from pypost.mappings import TFMapping
from pypost.data import DataManager
import numpy as np


class Function_Base(TFMapping):

    def __init__(self, dataManager, inputArguments, outputArguments, meanTensorGenerator, name = 'Function'):

        TFMapping.__init__(self, dataManager, inputArguments, outputArguments, name = name)

        self.meanTensorGenerator = meanTensorGenerator

        #self.setTensorsForVariables([self.mean])
        self.setMappingTensorNode(self.mean)
        self._setLayersFromTensor(self.mean)

        tfutils.initialize()

    def clone(self, name):

        clone = Function_Base(self.dataManager, self.inputVariables, self.outputVariables, self.meanTensorGenerator, name)
        clone.parameters = self.parameters
        return clone

    @TFMapping.TensorMethod(connectTensorToOutput=True)
    def mean(self):
        meanTensor = self.meanTensorGenerator(self.getAllInputTensor(), self.dimOutput)
        return meanTensor


class LinearFunction(Function_Base):

    def __init__(self, dataManager, inputArguments, outputArguments, useBias = True, name = 'Function'):

        Function_Base.__init__(self, dataManager, inputArguments, outputArguments, tfutils.linear_layer_generator(useBias), name = name)


if __name__ == "__main__":
    num_cpu = 1
    tf_config = tf.ConfigProto(inter_op_parallelism_threads=num_cpu, intra_op_parallelism_threads=num_cpu)
    session = tf.Session(config=tf_config)
    session.__enter__()


    dataManager = DataManager('data')
    dataManager.addDataEntry('states', 10)
    dataManager.addDataEntry('actions', 5)

    generatorMean = tfutils.continuous_MLP_generator([100, 100])
    generatorLogStd = tfutils.diagional_log_std_generator()

    function = LinearFunction(dataManager, ['states'], ['actions'])

    data = dataManager.createDataObject([10])

    data[...].states = np.random.normal(0, 1, data[...].states.shape)


