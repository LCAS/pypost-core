from pypost.common.SettingsClient import SettingsClient
from pypost.mappings.Mapping import Mapping


class BatchLearner(Mapping, SettingsClient):
    '''
    The Learner class serves as a base class for all learners and predefines
    all necessary methods.
    '''

    def __init__(self, dataManager):
        '''
        Constructor
        '''

        Mapping.__init__(self,dataManager, inputVariables=[], outputVariables=[])
        SettingsClient.__init__(self)
        self.iterations = 0

    @Mapping.MappingMethod(inputArguments=[], outputArguments=[], takesData=True)
    def updateModel(self, data):

        self.iterations += 1

    def printMessage(self, data):
        # placeholder
        print('Iteration {}:'.format(self.iterations))

