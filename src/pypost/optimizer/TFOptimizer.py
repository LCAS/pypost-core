import tensorflow as tf
import numpy as np
from pypost.mappings import Mapping
from pypost.mappings import TFMapping
from pypost.data import Data

from enum import Enum


class TFOptimizerType(Enum):
    Adam = 1
    GradientDescent = 2


class TFOptimizer(Mapping):

    def __init__(self, dataManager, lossFunction, variables_list = None, name = None, printIterations=False):
        super().__init__(dataManager)

        self.loss = lossFunction
        self.variables_list = variables_list

        if (name is None):
            self.name = ''
        else:
            self.name = name + '_'

        self.linkPropertyToSettings('tfOptimizerType', globalName = self.name + 'tfOptimizerType', defaultValue=TFOptimizerType.Adam)
        self.linkPropertyToSettings('tfOptimizerNumIterations', globalName = self.name + 'tfOptimizerNumIterations', defaultValue=1000)
        self.linkPropertyToSettings('tfOptimizerBatchSize', globalName=self.name + 'tfOptimizerBatchSize', defaultValue = -1)

        if self.tfOptimizerType == TFOptimizerType.Adam:

            self.linkPropertyToSettings('tfAdamLearningRate', globalName = self.name + 'tfAdamLearningRate', defaultValue = 0.001)
            self.linkPropertyToSettings('tfAdamBeta1', globalName=self.name + 'tfAdamBeta1',
                                        defaultValue=0.9)
            self.linkPropertyToSettings('tfAdamBeta2', globalName=self.name + 'tfAdamBeta2',
                                        defaultValue=0.999)
            self.linkPropertyToSettings('tfAdamEpsilon', globalName=self.name + 'tfAdamEpsilon',
                                        defaultValue=10**-8)

            self.optimizer = tf.train.AdamOptimizer(learning_rate = self.tfAdamLearningRate, beta1 = self.tfAdamBeta1,
                                                    beta2 = self.tfAdamBeta2, epsilon = self.tfAdamEpsilon)

        elif self.tfOptimizerType == TFOptimizerType.GradientDescent:

            self.linkPropertyToSettings('tfGradientLearningRate', globalName=self.name + 'tfGradientLearningRate', defaultValue=0.001)

            self.optimizer = tf.train.GradientDescentOptimizer(learning_rate=self.tfGradientLearningRate)

        self.minimize = self.optimizer.minimize(self.loss, var_list=self.variables_list)
        self.tm_minimize = TFMapping(dataManager, tensorNode = self.minimize)
        self.tm_loss = TFMapping(dataManager, tensorNode = self.loss)

        self._printIterations = printIterations
        self.lossLogger = []

    @Mapping.MappingMethod(takesData=True)
    def optimize(self, data):
        if (self._printIterations):
            print('Loss Iteration 0: ', data[...] >= self.loss)

        numElements = data.getNumElements(self.tm_minimize.inputVariables[0])

        if (self.tfOptimizerBatchSize == -1):
            mini_batch_indices = [list(range(0,numElements))]
        else:
            inds = np.arange(numElements)
            np.random.shuffle(inds)

            sections = list(np.arange(0, numElements, self.tfOptimizerBatchSize)[1:])
            mini_batch_indices = np.array_split(inds, sections)

        self.lossLogger = []
        self.lossLogger.append(data[...] >= self.loss)

        import time
        start = time.clock()

        inputData = data.getDataEntryList(self.tm_minimize.inputVariables, data.activeIndex)
        inputDataLoss = data.getDataEntryList(self.tm_loss.inputVariables, data.activeIndex)
        for i in range(0, self.tfOptimizerNumIterations):
            indices = list(mini_batch_indices[i % len(mini_batch_indices)])

            miniBatchInputData = [dataItem[indices,:] for dataItem in inputData]

            self.tm_minimize(*miniBatchInputData )

            if (self._printIterations):
                self.lossLogger.append(self.tm_loss(*inputDataLoss))
                print('\rLoss Iteration %i: %.4f ' % (i + 1, self.lossLogger[-1]), end="")

        print('Optimization Duration: ', (time.clock() - start))

