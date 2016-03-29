import numpy as np
from functions.Mapping import Mapping
from functions.Function import Function
from parametricModels.ParametricFunction import ParametricFunction
from learner.parameterOptimization.HyperParameterObject \
    import HyperParameterObject


class FunctionLinearInFeatures(Mapping, Function, ParametricFunction,
                               HyperParameterObject):
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

    def __init__(self, dataManager, outputVariable, inputVariables,
                 functionName, featureGenerator,
                 doInitWeights=True):
        '''
        :param dataManager: Datamanger to operate on
        :param outputVariable: dataset defining the output of the function
        :param inputVariables: dataset defining the input of the function
        :param functionName: name of the function
        :param featureGenerator: feature generator of the dataset
        :param doInitWeights: flag if weights and bias should be initiated
        '''
        if isinstance(outputVariable, list):
            raise ValueError('multiple outputVariables are not supported!',
                             outputVariable)

        self.dataManager = dataManager
        # TODO deprecated: remove outputVariable and use outputVariables[0]
        # instead
        self.outputVariable = outputVariable
        self.outputVariables = [outputVariable]
        self.inputVariables = None
        self.functionName = functionName
        self.featureGenerator = None
        self.doInitWeights = doInitWeights
        self.featureHasHyperParameters = False

        if featureGenerator is not None:
            raise ValueError('Features are not implemented yet.')

        # represents the liniar function as
        # y = weights * x + bias
        self.bias = None
        self.initSigmaMu = 0.01
        self.doInitWeights = doInitWeights
        self.initMu = []

        Mapping.__init__(self, dataManager, self.outputVariables, inputVariables,
                         functionName)
        Function.__init__(self)
        ParametricFunction.__init__(self)

        ''' FIXME
        if (ischar(self.outputVariables[0]))
            self.linkProperty('initSigmaMu', ['initSigmaMu',  upper(self.outputVariables[0](1)), self.outputVariables[0](2:end)]);
            self.linkProperty('initMu', ['initMu', upper(self.outputVariables[0][1]), self.outputVariable[0][2:end]]);
        else
            self.linkProperty('initSigmaMu');
            self.linkProperty('initMu');
        end
        '''

        self.registerMappingInterfaceFunction()
        self.registerGradientFunction()

        if self.doInitWeights:
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

    def getExpectation(self, numElements, inputFeatures=None):
        '''
        Returns the expectation of the Function.

        If the parameter inputFeatures is not given the function expect
        it to be zero and only returns the bias. Otherwise this function
        will return the weighted expectation.
        '''
        if len(self.bias.shape) >= 2:
            biasTrans = self.bias.conj().T
        else:
            biasTrans = self.bias[np.newaxis, :].T

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

        if len(self.bias.shape) > 1 and self.bias.shape[1] > 1:
            self.bias = self.bias.conj().T

    def setWeights(self, weights):
        if weights.shape != (self.dimOutput, self.dimInput):
            raise ValueError('invalid weights shape')

        self.weights = weights

    # Parametric Model Function
    def getNumParameters(self):
        return self.dataManager.getNumDimensions(self.outputVariables[0]) * \
            (1 + self.dataManager.getNumDimensions(self.inputVariables))

    def getGradient(self, inputMatrix):
        return np.hstack((np.ones((inputMatrix.shape[0], self.dimOutput)),
                          np.tile(inputMatrix, (1, self.dimOutput))))

    def setParameterVector(self, theta):
        self.weights = theta[1:]
        print('a', self.weights.shape)
        self.bias = theta[0, :].conj().T
        print('a', self.bias.shape)

    def getParameterVector(self):
        return np.vstack([self.bias, self.weights])
