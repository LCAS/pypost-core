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

    def FunctionLinearInFeatures(dataManager, outputVariable, inputVariables,
                                 functionName, featureGenerator,
                                 doInitWeights):
        '''
        :param dataManager: Datamanger to operate on
        :param outputVariable: dataset defining the output of the function
        :param inputVariables: dataset defining the input of the function
        :param functionName: name of the function
        :param featureGenerator: feature generator of the dataset
        :param doInitWeights: flag if weights and bias should be initiated
        '''
        self.featureGenerator = []
        self.featureHasHyperParameters = False;

        # represents the liniar function as
        # y = weights * x + bias
        self.bias = 0
        self.initSigmaMu = 0.01
        self.doInitWeights = True
        self.initMu = []

        Mapping(dataManager, outputVariable, inputVariables, functionName);
        Function();
        ParametricFunction();

        ''' FIXME
        if (ischar(outputVariable))
            obj.linkProperty('initSigmaMu', ['initSigmaMu',  upper(obj.outputVariable(1)), obj.outputVariable(2:end)]);
            obj.linkProperty('initMu', ['initMu', upper(obj.outputVariable(1)), obj.outputVariable(2:end)]);
        else
            obj.linkProperty('initSigmaMu');
            obj.linkProperty('initMu');
        end
        '''

        if featureGenerator is not None:
            self.setFeatureGenerator(featureGenerator)
        else:
            self.featureGenerator = ''

        if self.inputVariables is not None:
            if self.featureGenerator == [] and \
               dataManager.isFeature(self.inputVariables[1]):
                self.setFeatureGenerator(
                    self.dataManager.getFeatureGenerator(inputVariables[1]))

        self.doInitWeights = doInitWeights

        self.registerMappingInterfaceFunction();
        self.registerGradientFunction();

        if(self.doInitWeights):
            self.bias = np.zeros((self.dimOutput, 1))
            self.weights = np.zeros((self.dimOutput, self.dimInput))

            if len(self.initMu) == 0:
                Range = self.dataManager.getRange(self.outputVariable)
                meanRange = (self.dataManager.getMinRange(self.outputVariable)
                    + self.dataManager.getMaxRange(self.outputVariable)) / 2;

                self.bias  = (meanRange.conj().T + range.conj().T *\
                    self.initSigmaMu * (np.rand(self.dimOutput, 1) - 0.5))
            else:
                self.bias  = np.copy(self.initMu)
                if self.bias.size == 1 and self.dimOutput > 1:
                    # TODO
                    print('WARNING: Gaussian Distribution: Initializing mean with scalar, converting in vector\n');
                    self.bias = np.tile(self.bias, (self.dimOutput, 1))

                if self.bias.shape[1] > 1:
                    self.bias = self.bias.conj().T


        def setFeatureGenerator(self, featureGenerator):
            self.setInputVariables(featureGenerator.outputName)
            self.featureGenerator = featureGenerator
            self.featureHasHyperParameters = isinstance(featureGenerator,
                                                        HyperParameterObject)
            self.addDataManipulationFunction(
                'getExpectationGenerateFeatures',
                featureGenerator.featureVariables, [self.outputVariable], True,
                True)


        def getExpectationGenerateFeatures(self, numElements, varargin):
            '''
            Returns the expectation of the Function after generating the Features.
            '''

            inputFeatures = varargin[1];


            if self.featureGenerator is not None:
                inputFeatures = self.featureGenerator.getFeatures(
                    numElements, varargin[:])

            inputFeatures = self.featureGenerator.getFeatures(
                numElements, varargin[:])
            return self.getExpectation(numElements, inputFeatures)


        def getExpectation(self, numElements, inputFeatures):
            '''
            Returns the expectation of the Function.

            If the parameter inputFeatures is not given the function expect
            it to be zero and only returns the bias. Otherwise this function
            will return the weighted expectation.
            '''

            value = np.tile(obj.bias.conj().T, (numElements, 1))
            value = value + inputFeatures * self.weights.conj().T;
            return value

        def setWeightsAndBias(self, weights, bias):
            self.bias = bias
            self.weights = weights

            if self.bias.shape[1] > 1:
                self.bias = self.bias.conj().T

            if self.weights.shape[0] != self.dimOutput:
                self.weights = self.weights.conj().T

            # TODO: assert
            # assert(size(obj.weights,1) == obj.dimOutput && size(obj.weights,2) == obj.dimInput && size(obj.bias,1) == obj.dimOutput);

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
            return dataManager.getNumDimensions(self.outputVariable.dot()).dot(
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

        # XXX Is this needed anymore?
        #function [gradient] = getLikelihoodGradient(obj, varargin)
        #    assert(false);
        #end
