import numpy as np

from pypost.learner.InputOutputLearner import InputOutputLearner
from pypost.mappings import Mapping
from pypost.mappings import DataManipulator


class LinearFeatureFunctionMLLearner(InputOutputLearner):
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

        self.linkPropertyToSettings('regularizationRegression')

    @DataManipulator.DataMethod(inputArguments=['self.inputVariables', 'self.outputVariables', 'self.weightName'], outputArguments=[])
    def lossFunction(self, inputData, outputData, weighting = None):

        prediction = self.functionApproximator.output(inputData)
        if weighting:
            mse = np.sum(np.sum((prediction - outputData) ** 2, axis=1) * weighting)
        else:
            mse = np.sum(np.sum((prediction - outputData) ** 2, axis=1))
        return mse

    @Mapping.MappingMethod(inputArguments=['self.inputVariables', 'self.outputVariables', 'self.weightName'], outputArguments=[])
    def updateModel(self, inputData, outputData, weighting = None):
        if weighting is None:
            weighting = np.ones((outputData.shape[0], 1))

        inputData = self.functionApproximator.getLinearFeatures(inputData)

        numSamples = outputData.shape[0]

        if (self.outputDataNormalization):
            ''' if outputDataNormalization is set, transform the output mean to 0 and output range to[-1, 1] '''
            rangeOutput = self.dataManager.getRange(self.outputVariable)
            meanRangeOutput = (self.dataManager.getMinRange( self.outputVariable) + self.dataManager.getMaxRange(self.outputVariable)) / 2

            outputData = (outputData - meanRangeOutput) / rangeOutput

        inputStd = inputData.std(0)
        inputMean = inputData.mean(0)

        valididxs = np.logical_or(inputStd > 0, abs(inputMean) != 0)
        if inputData.shape[1] > 0 and self.inputDataNormalization:
            rangeInput = inputData.std(axis = 0)
            idx = rangeInput > 1e-10
            meanRangeInput = inputData.mean(axis = 0)

            inputData[:,  idx] = (inputData[:,  idx] - meanRangeInput[idx]) /  rangeInput[idx]


        Shat = inputData[:, valididxs]

        sumW = weighting.sum()
        weighting = weighting / sumW
        dimInput = Shat.shape[1] - 1

        SW = Shat * weighting

        regressionMatrix = np.zeros((Shat.shape[1],Shat.shape[1]))
        regressionMatrix[idx,idx] = 1
        matrixtoInvert = np.dot(SW.transpose(), Shat) + self.regularizationRegression * regressionMatrix

        thetaL = np.linalg.solve(matrixtoInvert, np.dot(SW.transpose(), outputData)).transpose()

        BetaA = thetaL

        if inputData.shape[1] > 0:
            if self.outputDataNormalization:
                BetaA = BetaA * rangeOutput.transpose()

        if self.inputDataNormalization and inputData.shape[1] > 0:

            BetaA[:, idx] = BetaA[:, idx] / rangeInput[idx]
            temp = np.dot(BetaA[:, idx], meanRangeInput[idx].transpose())

            BetaA[:, np.logical_not(idx)] = BetaA[:, np.logical_not(idx)] - temp[:, np.newaxis]

        #if self.outputDataNormalization:
        #    MuA = MuA * rangeOutput.transpose() + meanRangeOutput.transpose()

        self.functionApproximator.setLinearParameters(BetaA)
