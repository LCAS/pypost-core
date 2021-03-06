from pypost.learner.BatchLearner import BatchLearner
from pypost.mappings import Mapping
import tensorflow as tf
import pypost.common.tfutils as tfutils
from pypost.mappings import TFMapping
from pypost.optimizer.TFOptimizer import TFOptimizer
from pypost.optimizer.TFOptimizer import TFOptimizerType


class InputOutputLearner(BatchLearner):

    '''
    The Learner class serves as interface for all learners that learn an input output mapping.
    '''

    def __init__(self, dataManager, functionApproximator, weightName = None, inputVariables = None, outputVariable = None):
        '''
        Constructor
        :param dataManager: the data manager
        :param functionApproximator:
        :param weightName: name of the weight
        :param inputVariables: can be specified if different from input variables in functionApproximator
        :param outputVariable: can be specified if different from input variables in functionApproximator
        '''

        BatchLearner.__init__(self, dataManager)

        self.functionApproximator = functionApproximator
        self.weightName = weightName

        if self.functionApproximator is None:
            assert inputVariables is not None and outputVariable is not None, "pst:Supervised Learner: If no function approximator is provided you need to pass input and output Variables!"

        if inputVariables is not None:
            self.inputVariables = inputVariables
            if type(self.inputVariables) is list:
                self.inputVariables = [self.inputVariables]

        else:
            self.inputVariables = self.functionApproximator.inputVariables


        if outputVariable is not None:
            self.outputVariables = [outputVariable]
        else:
            self.outputVariables = self.functionApproximator.outputVariables


    def setInputVariablesFromMapping(self):
        if self.functionApproximator is not None:
            self.inputVariables = self.functionApproximator.inputVariables
            self.outputVariables = self.functionApproximator.outputVariables

    def setWeightName(self, weightName):
        self.weightName = weightName



    def isWeightedLearner(self):
        return self.weightName

    def getWeightName(self):
        return self.weightName

    @Mapping.MappingMethod(inputArguments=['self.inputVariables', 'self.outputVariables', 'self.weightName'], outputArguments=[])
    def updateModel(self, inputData, outputData, weighting=None):
        return


class L2GradientLearner(InputOutputLearner):
    '''
    The Learner class serves as interface for all learners that learn an input output mapping.
    '''

    def __init__(self, dataManager, functionApproximator, weightName=None, inputVariables=None, outputVariable=None):

        InputOutputLearner.__init__(self, dataManager, functionApproximator, weightName=weightName, inputVariables=inputVariables, outputVariable=outputVariable)

        self.optimizer = TFOptimizer(dataManager, self.tn_lossFunction, variables_list=self.functionApproximator.tv_variables_list)


    @TFMapping.TensorMethod()
    def lossFunction(self):
        labels = self.dataManager.createTensorForEntry(self.outputVariables[0])

        if self.weightName is not None:
            weighting = self.dataManager.createTensorForEntry(self.weightName)
            loss = tf.losses.mean_squared_error(labels, self.functionApproximator.tn_output, weighting)
        else:
            loss = tf.losses.mean_squared_error(labels, self.functionApproximator.tn_output)

        return loss

    @Mapping.MappingMethod(inputArguments=[], outputArguments=[], takesData=True)
    def updateModel(self, data):

        data >> self.optimizer


class CrossEntropyLossGradientLearner(InputOutputLearner):
    '''
    The Learner class serves as interface for all learners that learn an input output mapping.
    '''

    def __init__(self, dataManager, functionApproximator, labels = 'labels', weightName=None, inputVariables=None):
        InputOutputLearner.__init__(self, dataManager, functionApproximator, weightName=weightName, inputVariables=inputVariables, outputVariable=labels)
        self.linkPropertyToSettings('l2Regularizer', globalName=functionApproximator.name + 'l2Regularizer', defaultValue=10**-2)

        self.optimizer = TFOptimizer(dataManager, self.tn_lossFunction, variables_list=self.functionApproximator.tv_variables_list, name='ClassifierLeaner')


    @TFMapping.TensorMethod()
    def lossFunction(self):
        labels = self.dataManager.createTensorForEntry(self.outputVariables[0])

        if self.weightName is not None:
            weighting = self.dataManager.createTensorForEntry(self.weightName)
            loss = tf.reduce_sum(tf.nn.weighted_cross_entropy_with_logits(targets=labels,
                                                                          logits=self.functionApproximator.tn_logit,
                                                                          pos_weight=weighting))
        else:
            loss = tf.reduce_sum(tf.nn.sigmoid_cross_entropy_with_logits(labels=labels,
                                                                         logits=self.functionApproximator.tn_logit))
        loss = loss + self.l2Regularizer * tf.reduce_sum(self.functionApproximator.getParamsFlatTensor() ** 2)

        return loss

    @Mapping.MappingMethod(inputArguments=[], outputArguments=[], takesData=True)
    def updateModel(self, data):
        data >> self.optimizer


class LogLikeGradientLearner(InputOutputLearner):
    '''
    The Learner class serves as interface for all learners that learn an input output mapping.
    '''

    def __init__(self, dataManager, functionApproximator, weightName=None, inputVariables=None, outputVariable=None):

        InputOutputLearner.__init__(self, dataManager, functionApproximator, weightName=weightName, inputVariables=inputVariables, outputVariable=outputVariable)

        self.optimizer = TFOptimizer(dataManager, self.tn_lossFunction, variables_list=self.functionApproximator.tv_variables_list)

    @TFMapping.TensorMethod()
    def lossFunction(self):
        if self.weightName is not None:
            weighting = self.dataManager.createTensorForEntry(self.weightName)
            loss = - tf.reduce_sum(tf.multiply(weighting, self.functionApproximator.tn_logLike), axis = 0)
        else:
            loss = - tf.reduce_sum(self.functionApproximator.tn_logLike, axis=0)

        return loss

    @Mapping.MappingMethod(inputArguments=[], outputArguments=[], takesData=True)
    def updateModel(self, data):

        data >> self.optimizer

