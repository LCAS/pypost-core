class AbstractInputOutputLearner(object):

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

        self.functionApproximator = functionApproximator
        self.additionalInputArguments = []

        if weightName is not None and weightName == True:
            self.weightName = [weightName]
        else:
            self.weightName = []

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


        self.setAdditionalInputArguments()

        self.registerLearnFunction()


    def setInputVariablesFromMapping(self):
        if self.functionApproximator is not None:
            self.inputVariables = self.functionApproximator.inputVariables
            self.outputVariable = self.functionApproximator.outputVariable
            self.registerLearnFunction()

    def setWeightName(self, weightName):
        self.weightName = [weightName]
        self.registerLearnFunction()



    def isWeightedLearner(self):
        if self.weightName:
            return True
        else:
            return False

    def getWeightName(self):
        return self.weightName[0]


    def setInputVariablesForLearner(self, *args):
        self.inputVariables = list(*args)
        self.registerLearnFunction()


    def setOutputVariableForLearner(self, outputVariable):
        self.outputVariable = outputVariable
        self.registerLearnFunction()


    def setFunctionApproximator(self, funcApprox):
        self.functionApproximator = funcApprox

    def setAdditionalInputArguments(self, *args):
        if self.functionApproximator is not None:
            self.additionalInputArguments = self.functionApproximator.additionalInputVariables
        else:
            self.additionalInputArguments = []
        self.additionalInputArguments = self.additionalInputArguments +  list(args)
        self.registerLearnFunction()

    def registerLearnFunction(self):
        raise NotImplementedError

