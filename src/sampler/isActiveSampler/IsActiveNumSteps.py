from sampler.isActiveSampler.IsActiveStepSampler import IsActiveStepSampler
from common.SettingsClient import SettingsClient



class IsActiveNumSteps(IsActiveStepSampler, SettingsClient):
    '''
    The sampler is active until to number of steps is reached

    Methods (annotated):
    def __init__(self, dataManager: data.DataManager, stepName: str =None, numTimeSteps: int =40) -> None
    def getNumTimeSteps(self) -> int
    def setNumTimeSteps(self, numTimeSteps: int) -> None
    def isActiveStep(self, nextStates, timeSteps: int) -> Boolean
    def toReserve(self) -> int
    '''

    def __init__(self, dataManager, stepName, numTimeSteps=40):
        '''
        Registers itself to the DataManipulator
        :param dataManager: The data manager to use
        :param stepName: Name of the steps to operate on (default: "timeSteps")
        :param numTimeSteps: number of time steps to run

        :change: new parameter for timesteps, since 40 is a magic number
        #FIXME default numTimeSteps value is still a magic number
        '''
        IsActiveStepSampler.__init__(self, dataManager, stepName)
        SettingsClient.__init__(self)

        self.numTimeSteps = numTimeSteps
        '''
        Number of timesteps to run
        '''

        self.resetProb = 1 / self.numTimeSteps
        '''
        Probability of a time step to reset
        '''
        if stepName is None:
            stepName = "timeSteps"
        self.linkProperty('resetProb', 'resetProb' + stepName.capitalize())
        self.linkProperty("numTimeSteps", "num" + stepName.capitalize())

    # getter & setters

    def getNumTimeSteps(self):
        '''
        Get the number of timesteps
        :returns: number of time steps
        '''
        return self.numTimeSteps

    def setNumTimeSteps(self, numTimeSteps):
        '''
        Set the number of timesteps
        :param numTimeSteps: number of timesteps to set
        :raises: RunTimeException: If the number of timesteps is negative
        '''
        if numTimeSteps < 0:
            raise RuntimeError("The number has to be equal or greater to 0")
        self.numTimeSteps = numTimeSteps

    def isActiveStep(self, nextStates, timeSteps):
        '''
        Returns if the time step is still active
        :param nextStates: data of the nextStates
        :param timeSteps: number of time steps
        :returns: True if the timestep if still active, False otherwise
        '''
        return (timeSteps < self.numTimeSteps)

    def toReserve(self):
        '''
        Get the number of timesteps to reserve
        :returns: Number of timesteps to reserve
        '''
        return self.getNumTimeSteps()
