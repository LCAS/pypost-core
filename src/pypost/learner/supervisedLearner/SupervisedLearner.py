from pypost.learner.Learner import Learner
from pypost.data.DataManipulator import DataManipulator
from pypost.learner.AbstractInputOutputLearner import AbstractInputOutputLearner

class SupervisedLearner(Learner, AbstractInputOutputLearner, DataManipulator):

    ''' The SupervisedLearner serves as a base class for all supervised learners. It inherits from the AbstractInputOutputLearner and
    implements the standard Learner interface. The learning functionality needs to be implemented in the function 'learnFunction' which
    is automatically called with the correct data that has been registered in registerLearnFunction
    '''

    def __init__(self, dataManager, functionApproximator,  weightName = "", inputVariables = None, outputVariable = None):
        '''
        Constructor
        :param dataManager:
        :param functionApproximator:
        :param weightName:
        :param inputVariables:
        :param outputVariable:
        '''

        Learner.__init__(self)
        DataManipulator.__init__(self, dataManager)
        AbstractInputOutputLearner.__init__(self, dataManager, functionApproximator, weightName, inputVariables, outputVariable)


    def updateModel(self, data):
        self.callDataFunction('learnFunction', data)

    def learnFunction(self, inputData, outputData, varargin):
        raise NotImplementedError

    def registerLearnFunction(self):
        if self.inputVariables is None:
            inputVariablesTemp = ['']
        else:
            inputVariablesTemp = self.inputVariables

        self.addDataManipulationFunction(self.learnFunction, inputVariablesTemp + self.outputVariables + self.additionalInputArguments + self.weightName, [])
