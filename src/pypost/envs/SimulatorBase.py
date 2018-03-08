from pypost.mappings.DataManipulator import DataManipulator
from pypost.mappings.Mapping import Mapping


class SimulatorBase(Mapping):

    def __init__(self, dataManager, stateDim, actionDim):

        subDataManager = dataManager.subDataManager

        if stateDim > 0:
            subDataManager.addDataEntry('states', stateDim)
        else:
            subDataManager.addDataAlias('states', [])

        if actionDim > 0:
            subDataManager.addDataEntry('actions', actionDim)
        else:
            subDataManager.addDataAlias('actions', [])


        super().__init__(dataManager, ['actions'], ['nextStates'])

        self.stateDim = None
        self.actionDim = None

        self.minRangeAction = None
        self.maxRangeAction = None


    @Mapping.MappingMethod()
    def step(self, actions):
        return

    @DataManipulator.DataMethod(inputArguments=[],outputArguments='states')
    def reset(self):
        return
