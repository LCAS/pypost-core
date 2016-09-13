from pypost.learner.InputOutputLearner import InputOutputLearner
from pypost.parameterOptimization.HyperParameterObject import HyperParameterObject
import numpy as np
from pypost.data.DataManipulator import DataManipulator

class LinearFeatureFunctionMLLearner(InputOutputLearner, HyperParameterObject):
    ''' The LinearFeatureFunctionMLLearner fits a linear model using a weighted maximum likelihood estimate. It implements the
    supervised learner interface, i.e., the learning functionality is implemented in the method learnFunction
    The flags < tt > inputDataNormalization < / tt > and < tt > outputDataNormalization < / tt > determine if the
    the function < tt > learnFunction() < / tt > will normalize the input and output data to < tt > sigma = 1 < / tt >
    and < tt > mean = 0 < / tt > respectively.
    '''

    def __init__(self, dataManager, functionApproximator,  weightName = None, inputVariables = None, outputVariable = None):
        '''

        :param dataManager:
        :param functionApproximator:
        :param weightName:
        :param inputVariables:
        :param outputVariable:
        '''

        self.inputDataNormalization = True
        self.outputDataNormalization = False

        self.regularizationRegression = 10 ** -10

        InputOutputLearner.__init__(self, dataManager, functionApproximator, weightName, inputVariables, outputVariable);

        self.linkProperty('regularizationRegression')

    @DataManipulator.DataMethod(inputArguments=['self.inputVariables', 'self.outputVariables', 'self.weightName'], outputArguments=[])
    def updateModel(self, inputData, outputData, weighting = None):
        if weighting is None:
            weighting = np.ones((outputData.shape[0], 1))

        numSamples = outputData.shape[0]

        if (self.outputDataNormalization):
            ''' if outputDataNormalization is set, transform the output mean to 0 and output range to[-1, 1] '''
            rangeOutput = self.dataManager.getRange(self.outputVariable)
            meanRangeOutput = (self.dataManager.getMinRange( self.outputVariable) + self.dataManager.getMaxRange(self.outputVariable)) / 2

            outputData = (outputData - meanRangeOutput) / rangeOutput

        if inputData.shape[1] > 0 and self.inputDataNormalization:
            rangeInput = inputData.std(axis = 0)
            rangeInput[rangeInput < 1e-10] = 1e-10
            meanRangeInput = inputData.mean(axis = 0)

            inputData = (inputData - meanRangeInput) /  rangeInput

        valididxs = inputData.std(0) > 0

        if inputData.shape[1] > 0:
            Shat = np.hstack((np.ones((numSamples, 1)), inputData[:, valididxs]))
        else:
            Shat = np.ones((numSamples, 1))

        sumW = weighting.sum()
        weighting = weighting / sumW
        dimInput = Shat.shape[1] - 1

        SW = Shat * weighting

        regressionMatrix = np.identity(dimInput + 1)
        regressionMatrix[0,0] = 0
        matrixtoInvert = np.dot(SW.transpose(), Shat) + self.regularizationRegression * regressionMatrix

        thetaL = np.linalg.solve(matrixtoInvert, np.dot(SW.transpose(), outputData)).transpose()

        MuATemp = thetaL[:, 0]
        MuA = MuATemp[:, np.newaxis]

        BetaA = np.zeros((outputData.shape[1], inputData.shape[1]))

        if inputData.shape[1] > 0:
            BetaA[:, valididxs]  = thetaL[:, 1:]
            if self.outputDataNormalization:
                BetaA = BetaA * rangeOutput.transpose()

        if self.inputDataNormalization and inputData.shape[1] > 0:
            temp = np.dot(BetaA, meanRangeInput.transpose())
            MuA = MuA - temp[:,np.newaxis]
            BetaA = BetaA / rangeInput

        if self.outputDataNormalization:
            MuA = MuA * rangeOutput.transpose() + meanRangeOutput.transpose()


        self.functionApproximator.setWeightsAndBias(BetaA, MuA)