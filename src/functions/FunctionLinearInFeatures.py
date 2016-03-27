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
        self.outputVariable = outputVariable
        self.inputVariables = None
        self.functionName = functionName
        self.featureGenerator = None
        self.doInitWeights = doInitWeights
        self.featureHasHyperParameters = False

        # represents the liniar function as
        # y = weights * x + bias
        self.bias = None
        self.initSigmaMu = 0.01
        self.doInitWeights = doInitWeights
        self.initMu = []

        Mapping.__init__(self, dataManager, [outputVariable], inputVariables,
                         functionName)
        Function.__init__(self)
        ParametricFunction.__init__(self)

        ''' FIXME
        if (ischar(outputVariable))
            self.linkProperty('initSigmaMu', ['initSigmaMu',  upper(self.outputVariable(1)), self.outputVariable(2:end)]);
            self.linkProperty('initMu', ['initMu', upper(self.outputVariable(1)), self.outputVariable(2:end)]);
        else
            self.linkProperty('initSigmaMu');
            self.linkProperty('initMu');
        end
        '''

        if featureGenerator is not None:
            self.setFeatureGenerator(featureGenerator)

        if self.inputVariables is not None:
            if self.featureGenerator == [] and \
               dataManager.isFeature(self.inputVariables[1]):
                self.setFeatureGenerator(
                    self.dataManager.getFeatureGenerator(inputVariables[1]))


        self.registerMappingInterfaceFunction()
        self.registerGradientFunction()

        if self.doInitWeights:
            self.bias = np.zeros((self.dimOutput, 1))
            self.weights = np.zeros((self.dimOutput, self.dimInput))

            if len(self.initMu) == 0:
                minRange = self.dataManager.getMinRange(self.outputVariable)
                maxRange = self.dataManager.getMaxRange(self.outputVariable)
                range_diff = np.subtract(maxRange, minRange)

                meanRange = np.mean(np.array([minRange, maxRange]), axis=0)

                if len(meanRange.shape) != 1:
                    raise ValueError('Unsupported meanRange shape!')

                if len(range_diff.shape) != 1:
                    raise ValueError('Unsupported range_diff shape!')

                self.bias  = (
                    meanRange[np.newaxis, :].T +\
                    range_diff[np.newaxis, :].T *\
                    self.initSigmaMu * (np.random.rand(
                        self.dimOutput, 1) - 0.5))

            else:
                self.bias  = np.copy(self.initMu)
                if self.bias.size == 1 and self.dimOutput > 1:
                    # TODO
                    print('WARNING: Gaussian Distribution: Initializing mean with scalar, converting in vector\n');
                    self.bias = np.tile(self.bias, (self.dimOutput, 1))

                if self.bias.shape[1] > 1:
                    self.bias = self.bias.conj().T
                else:
                    raise ValueError('Better check the code twice!')


    def setFeatureGenerator(self, featureGenerator):
        self.setInputVariables(featureGenerator.outputName)
        self.featureGenerator = featureGenerator
        self.featureHasHyperParameters = isinstance(featureGenerator,
                                                    HyperParameterObject)
        self.addDataManipulationFunction(
            'getExpectationGenerateFeatures',
            featureGenerator.featureVariables, [self.outputVariable], True,
            True)


    def getExpectationGenerateFeatures(self, numElements, *args):
        '''
        Returns the expectation of the Function after generating the Features.
        '''
        if self.featureGenerator is not None:
            inputFeatures = self.featureGenerator.getFeatures(
                numElements, *args)
        else:
            inputFeatures = args[0]

        inputFeatures = self.featureGenerator.getFeatures(
            numElements, *args)
        return self.getExpectation(numElements, inputFeatures)


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
            raise ValueError('weight are a vector. This is not handled by the code')

        if inputFeatures is not None:
            print('FunctionLinearInFeatures: inputFeatures is None')
            mult = inputFeatures.dot(self.weights.conj().T)
            value = value + mult

        return value

    def setWeightsAndBias(self, weights, bias):
        self.bias = bias
        self.weights = weights

        if self.bias.shape[1] > 1:
            self.bias = self.bias.conj().T

        if self.weights.shape[0] != self.dimOutput:
            self.weights = self.weights[np.newaxis, :].T

        if self.weights.shape[0] != self.dimOutput: #pragma no branch
            raise ValueError('Invalid weights shape!')

        # TODO: assert
        raise RuntimeError('asserts are not implemented')
        # assert(size(self.weights,1) == self.dimOutput && size(self.weights,2) == self.dimInput && size(self.bias,1) == self.dimOutput);

    def setBias(self, bias):
        self.bias = bias;
        if self.bias.shape[1] > 1:
            self.bias = self.bias.conj().T

    ### Hyper Parameter Functions

    def getNumHyperParameters(self):
        if self.featureHasHyperParameters:
            return self.featureGenerator.getNumHyperParameters()
        else:
            return 0

    def setHyperParameters(self, params):
        if self.featureHasHyperParameters:
            self.featureGenerator.setHyperParameters(params)

    def getHyperParameters(self):
        if self.featureHasHyperParameters:
            return self.featureGenerator.getHyperParameters();
        else:
            return []

    def getExpParameterTransformMap(self):
        if self.featureHasHyperParameters:
            return self.featureGenerator.getExpParameterTransformMap()
        else:
            return [] # TODO check this. was: logical([])

    ### Parametric Model Function
    def getNumParameters(self):
        return dataManager.getNumDimensions(self.outputVariable).dot(
            1 + dataManager.getNumDimensions(self.inputVariables))

    def getGradient(self, inputMatrix):
        return np.hstack((np.ones(inputMatrix.shape[0], self.dimOutput),
                          np.tile(inputMatrix, (1, self.dimOutput))));

    def setParameterVector(self, theta):
        self.bias = theta[0:self.dimOutput].conj().T
        self.weights = theta[
            self.dimOutput,
            self.dimOutput + (self.dimInput.dot(self.dimOutput))]\
            .reshape(self.dimOutput, self.dimInput, order='F')

    def getParameterVector(self):
        return np.hstack([self.bias, self.weights[:]])

    # TODO Is this needed anymore?
    #function [gradient] = getLikelihoodGradient(self, varargin)
    #    assert(False);
    #end
