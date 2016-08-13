from pypost.data.DataManipulator import DataManipulator
from pypost.common.SettingsClient import SettingsClient

class BatchLearner(DataManipulator, SettingsClient):
    '''
    The Learner class serves as a base class for all learners and predefines
    all necessary methods.
    '''

    def __init__(self, dataManager):
        '''
        Constructor
        '''

        DataManipulator.__init__(self,dataManager)
        SettingsClient.__init__(self)

    @DataManipulator.DataManipulationMethod(inputArguments=[], outputArguments=[], takesData=True)
    def updateModel(self, data):
        raise NotImplementedError("Not implemented")

    def printMessage(self, data):
        raise NotImplementedError("Not implemented")

