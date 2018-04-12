import tensorflow as tf
import pypost.common.tfutils as tfutils
from pypost.mappings import TFMapping
from pypost.data import DataManager
import numpy as np
from pypost.mappings.Function import QuadraticFeatureExpansion

class SigmoidClassifier_Base(TFMapping):

    def __init__(self, dataManager, inputArguments, outputArguments, name = 'Classifier'):

        TFMapping.__init__(self, dataManager, inputArguments, outputArguments, name = name)

    def clone(self, name):

        clone = SigmoidClassifier_Base(self.dataManager, self.inputVariables, self.outputVariables, self.outputTensorGenerator, name)
        clone.params = self.params
        return clone

    @TFMapping.TensorMethod()
    def logit(self):
        raise NotImplementedError()
        #output = self.outputTensorGenerator(self.getAllInputTensor(), self.dimOutput)
        return

    @TFMapping.TensorMethod(connectTensorToOutput=True, useAsMapping=True)
    def predict(self):
        return tf.sigmoid(self.tn_logit)

    @TFMapping.TensorMethod(useAsMapping=False)
    def sample(self):
        z = tf.random_uniform(tf.shape(self.tn_logit), minval=0, maxval=1)

        return tf.cast(tf.greater(z, self.tn_logit), tf.int32)

class LinearClassifier(SigmoidClassifier_Base):

    def __init__(self, dataManager, inputArguments, outputArguments, useBias = True, name = 'Classifier'):
        SigmoidClassifier_Base.__init__(self, dataManager, inputArguments, outputArguments, name = name)
        self.useBias = useBias

    @TFMapping.TensorMethod(connectTensorToOutput=True)
    def logit(self):
        return tfutils.create_linear_layer(self.getAllInputTensor(), self.dimOutput, self.useBias)

    def clone(self, name, inputVariables = None):

        if inputVariables is None:
            inputVariables = self.inputVariables

        clone = LinearClassifier(self.dataManager, inputVariables, self.outputVariables, name)
        clone.params = self.params
        return clone


class QuadraticClassifier(LinearClassifier):

    def __init__(self, dataManager, inputArguments, outputArguments, name = 'Classifier'):
        self.quadraticFeatures = QuadraticFeatureExpansion(dataManager, inputArguments=inputArguments)
        LinearClassifier.__init__(self, dataManager, self.quadraticFeatures.outputVariables, outputArguments, useBias = False, name = name)


    def clone(self, name, inputVariables = None):

        if inputVariables is None:
            inputVariables = self.inputVariables

        clone = QuadraticClassifier(self.dataManager, inputVariables, self.outputVariables, name)
        clone.params = self.params
        return clone

class MLPClassifier(SigmoidClassifier_Base):

    def __init__(self, dataManager, inputArguments, outputArguments, hiddenNodes, name = 'Classifier'):
        SigmoidClassifier_Base.__init__(self, dataManager, inputArguments, outputArguments, name = name)
        self.hiddenNodes = hiddenNodes

    @TFMapping.TensorMethod(connectTensorToOutput=True)
    def logit(self):
        return tfutils.create_layers_linear_ouput(self.getAllInputTensor(), self.hiddenNodes, 1)

    def clone(self, name, inputVariables = None):

        if inputVariables is None:
            inputVariables = self.inputVariables

        clone = MLPClassifier(self.dataManager, inputVariables, self.outputVariables, hiddenNodes = self.hiddenNodes, name = name)
        clone.params = self.params
        return clone



if __name__ == "__main__":
    num_cpu = 1
    tf_config = tf.ConfigProto(inter_op_parallelism_threads=num_cpu, intra_op_parallelism_threads=num_cpu)
    session = tf.Session(config=tf_config)
    session.__enter__()

    dataManager = DataManager('data')
    dataManager.addDataEntry('states', 10)
    dataManager.addDataEntry('predictions', 1)

    generatorMean = tfutils.continuous_MLP_generator([100, 100])
    generatorLogStd = tfutils.diagional_log_std_generator()

    function = LinearClassifier(dataManager, ['states'], ['predictions'])

    data = dataManager.createDataObject([10])

    data[...].states = np.random.normal(0, 1, data[...].states.shape)


