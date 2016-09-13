from pypost.learner.BatchLearner import BatchLearner

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
            self.outputVariable = self.functionApproximator.outputVariable

    def setWeightName(self, weightName):
        self.weightName = weightName



    def isWeightedLearner(self):
        return self.weightName

    def getWeightName(self):
        return self.weightName



