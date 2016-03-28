from data.DataManipulator import DataManipulator


class IsActiveStepSampler(DataManipulator):
    '''
    IsActiveStepSampler determines whether a sequence is still active
    e.g. whether it is not reset

    Methods (annotated):
    def __init__(self, dataManager: data.DataManager, stepName: str) -> None
    def isActiveStep(self, nextStates, timeSteps: int) -> None
    '''

    def __init__(self, dataManager, stepName):
        '''
        Registers itself to the DataManipulator
        :param dataManager: The data manager to use
        :param stepName: Name of the steps to operate on (default: "timeSteps")
        '''

        # FIXME DataManipulator interface needs a setDataManager function or a
        # constructor interface
        #self.setDataManager(dataManager)
        super().__init__(dataManager)

        if stepName is None:
            stepName = "timeSteps"
        self.addDataManipulationFunction(
            self.isActiveStep, {"nextStates", stepName}, 'isActive')

    def isActiveStep(self, nextStates, timeSteps):
        '''
        Returns if the time step is still active
        :param nextStates: data of the nextStates
        :param timeSteps: number of time steps
        :returns: True if the timestep if still active, False otherwise
        '''
        raise NotImplementedError("Not implemented")

    def toReserve(self):
        '''
        Get the number of timesteps to reserve
        :returns: Number of timesteps to reserve
        '''
        raise NotImplementedError("Not implemented")
