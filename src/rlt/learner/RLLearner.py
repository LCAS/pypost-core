from rlt.learner.Learner import Learner


class RLLearner(Learner):
    '''
    Base class for reinforcement learners
    '''

    def __init__(self):
        '''
        Constructor
        '''

        Learner.__init__(self)

    def printMessage(self, data):
        # FIXME refactor everything in the line below ...
        # FIXME replace magic constant returns by settings
        print("Average Return: %f", np.mean(data.getDataEntry("returns")))
