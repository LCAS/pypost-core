import numpy as np

from pypost.common.SettingsClient import SettingsClient
from pypost.learner.parameterOptimization.HyperParameterObject import HyperParameterObject
from pypost.mappings.Function import Function


class FunctionLinearInFeatures(Function, HyperParameterObject, SettingsClient):
    '''
    TODO: check documentation
    The FunctionLinearInFeatures is a subclass of mapping and implements
    the Function interface. It models a multidimensional linear function.

    Since this class is a subclass of mapping you need to define a
    datamananger to operate on as well as a set of output and input
    variables and a function Name (See Functions.Mapping for more
    information about mappings).

    This class will save the linear function it represents in the variables
    weights and bias, where weights is the coefficient matrix of the
    function and bias its offset. As Equation:
    \f[
        \boldsymbol{y} = \boldsymbol{W} \boldsymbol{\phi}(\boldsymbol{x}) +
        \boldsymbol{b},
    \f]
    where \f$\boldsymbol{W}\f$ is represented by the variable weights and
    \f$\boldsymbol{b}\f$ by the variable bias.
    '''

    def __init__(self, dataManager,  inputVariables, outputVariable,
                 functionName, featureGenerator = None,
                 doInitWeights=True):
        '''
        :param dataManager: Datamanger to operate on
        :param outputVariable: dataset defining the output of the function
        :param inputVariables: dataset defining the input of the function
        :param functionName: name of the function
        :param featureGenerator: feature generator of the dataset
        :param doInitWeights: flag if weights and bias should be initiated
        '''
        SettingsClient.__init__(self)

        self.featureGenerator = None
        self.featureHasHyperParameters = False

        self.doInitWeights = doInitWeights

        Function.__init__(self, dataManager, inputVariables, outputVariable, functionName)

        if featureGenerator is not None:
            raise ValueError('Features are not implemented yet.')

        # represents the liniar function as
        # y = weights * x + bias
        self.bias = None
        self.initSigmaMu = 0.01
        self.doInitWeights = doInitWeights
        self.initMu = []

        if isinstance(self.outputVariables[0], str):
            self.linkProperty('initSigmaMu', 'initSigmaMu' + self.outputVariables[0].capitalize())
            self.linkProperty('initMu', 'initMu' + self.outputVariables[0].capitalize())
        else:
            self.linkProperty('initSigmaMu')
            self.linkProperty('initMu')

        if self.doInitWeights:
            self.initialize()

    def initialize(self):
        self.bias = np.zeros((self.dimOutput, 1))
        self.weights = np.zeros((self.dimOutput, self.dimInput))

        if len(self.initMu) == 0:
            minRange = self.dataManager.getMinRange(
                self.outputVariables[0])
            maxRange = self.dataManager.getMaxRange(
                self.outputVariables[0])
            range_diff = np.subtract(maxRange, minRange)

            meanRange = np.mean(np.array([minRange, maxRange]), axis=0)

            if len(meanRange.shape) != 1:  # pragma nocover
                raise ValueError('Unsupported meanRange shape')

            if len(range_diff.shape) != 1:  # pragma nocover
                raise ValueError('Unsupported range_diff shape')

            self.bias = (
                meanRange[np.newaxis, :].T +
                range_diff[np.newaxis, :].T *
                self.initSigmaMu * (np.random.rand(
                    self.dimOutput, 1) - 0.5))

        else:
            raise ValueError('Unsupported initMu shape')  # pragma nocover

    def computeOutput(self, inputFeatures):
        '''
        Returns the expectation of the Function.

        If the parameter inputFeatures is not given the function expect
        it to be zero and only returns the bias. Otherwise this function
        will return the weighted expectation.
        '''

        # if we do not have input variables, the inputFeatures will be set to the number of elements to return
        numElements, inputFeatures = self.getNumElementsAndInput(inputFeatures)


        biasTrans = self.bias.conj().T

        value = np.tile(biasTrans, (numElements, 1))

        if len(self.weights.shape) == 1:
            raise ValueError(
                'weight are a vector. This is not handled by the code')

        if inputFeatures is not None:
            mult = inputFeatures.dot(self.weights.conj().T)
            value = value + mult

        return value

    def setWeightsAndBias(self, weights, bias):
        self.setBias(bias)
        self.setWeights(weights)

    def setBias(self, bias):
        if bias.shape[0] != self.dimOutput:
            raise ValueError('invalid bias shape')

        self.bias = bias
        if (len(self.bias.shape) == 1):
            self.bias.resize(self.bias.shape[0],1)

        if len(self.bias.shape) > 1 and self.bias.shape[1] > 1:
            self.bias = self.bias.conj().T

    def setWeights(self, weights):
        if weights.shape != (self.dimOutput, self.dimInput):
            raise ValueError('invalid weights shape')

        self.weights = weights

