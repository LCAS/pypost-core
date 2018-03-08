from pypost.mappings.DataManipulator import DataManipulator
from pypost.mappings.Mapping import Mapping


# Todo Periodicity!

class TransitionFunction(Mapping):

    def __init__(self, dataManager, stateDim, actionDim):

        subDataManager = dataManager.subDataManager

        subDataManager.addDataEntry('states', stateDim)
        subDataManager.addDataEntry('actions', actionDim)

        super().__init__(dataManager, ['states', 'actions'], ['nextStates'])

        self.stateDim = None
        self.actionDim = None

        self.minRangeAction = None
        self.maxRangeAction = None

    @DataManipulator.DataMethod(inputArguments=['contexts'], outputArguments=['states'])
    def initStateFromContexts(self, contexts):
        return contexts[:, 0: self.stateDim]

    @Mapping.MappingMethod()
    def transitionFunction(self, states, actions):
        return

    def getStateDifference(self, state1, state2):
        stateDiff = (state1 - state2)
        return stateDiff

    def projectStateInPeriod(self, state):
        # todo implement, no periodicity feature in data manager
        raise RuntimeError('Not yet Implemented')

