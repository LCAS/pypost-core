from pypost.sampler.TerminationFunction import TerminationFunction
from pypost.common.SettingsClient import SettingsClient


class NumStepsTerminationFunction(TerminationFunction, SettingsClient):
    '''
    The sampler is active until to number of steps is reached

    Methods (annotated):
    def __init__(self, dataManager: data.DataManager, stepName: str =None, numTimeSteps: int =40) -> None
    def getNumTimeSteps(self) -> int
    def setNumTimeSteps(self, numTimeSteps: int) -> None
    def isActiveStep(self, nextStates, timeSteps: int) -> Boolean
    def toReserve(self) -> int
    '''
    # Todo make numTimeSteps settable via settings or constructor, but both?
    def __init__(self, dataManager, stepName = 'timeSteps', numTimeSteps = None):
        '''
        Registers itself to the DataManipulator
        :param dataManager: The data manager to use
        :param stepName: Name of the steps to operate on (default: "timeSteps")
        :param numTimeSteps: number of time steps to run

        :change: new parameter for timesteps, since 40 is a magic number
        #FIXME default numTimeSteps value is still a magic number
        '''
        TerminationFunction.__init__(self, dataManager, stepName)
        SettingsClient.__init__(self)

        self.numTimeSteps = 10


        '''
        Number of timesteps to run
        '''

        if stepName is None:
            stepName = "timeSteps"

        if (numTimeSteps):
            self.numTimeSteps = numTimeSteps
            self.linkPropertyToSettings("numTimeSteps", "num" + stepName[0].upper() + stepName[1:], True)
        else:
            self.linkPropertyToSettings("numTimeSteps", "num" + stepName[0].upper() + stepName[1:])

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

    def isNonTerminalState(self, nextStates, timeSteps):
        '''
        Returns if the time step is still active
        :param nextStates: data of the nextStates
        :param timeSteps: number of time steps
        :returns: True if the timestep if still active, False otherwise
        '''
        return (timeSteps < self.numTimeSteps - 1)

    def toReserve(self):
        '''
        Get the number of timesteps to reserve
        :returns: Number of timesteps to reserve
        '''
        return self.getNumTimeSteps()
