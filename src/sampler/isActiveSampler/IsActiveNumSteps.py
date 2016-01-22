'''
Created on 24.11.2015

@author: Moritz
'''
from sampler.isActiveSampler import IsActiveStepSampler


class IsActiveNumSteps(IsActiveStepSampler):
    '''
    The sampler is active until to number of steps is reached
    '''

    def __init__(self, dataManager, stepName=None, numTimeSteps=40):
        '''
        Registers itself to the DataManipulator
        @param dataManager: The data manager to use
        @param stepName: Name of the steps to operate on (default: "timeSteps")
        @param numTimeSteps: number of time steps to run

        @change: new parameter of timesteps, since 40 is a magic number
        #FIXME default numTimeSteps value is still a magic number
        '''
        super().__init__(dataManager, stepName)

        self._numTimeSteps = numTimeSteps
        '''
        Number of timesteps to run
        '''

        self._resetProb = 1 / self._numTimeSteps
        '''
        Probability of a time step to reset
        '''

        self._resetProbName = None
        '''
        FIXME
        '''

        # ASK Why is "num" needed. magical constant.
        self.linkProperty(
            "numTimeSteps", ["num", stepName[0].upper(), stepName[1:]])

    # getter & setters

    def getNumTimeSteps(self):
        '''
        Get the number of timesteps
        @return: number of time steps
        '''
        return self._numTimeSteps

    def setNumTimeSteps(self, numTimeSteps):
        '''
        Set the number of timesteps
        @param numTimeSteps: number of timesteps to set
        @raise RunTimeException: If the number of timesteps is negative
        '''
        if numTimeSteps < 0:
            raise RuntimeError("The number has to be equal or greater to 0")
        self._numTimeSteps = numTimeSteps

    def isActiveStep(self, nextStates, timeSteps):
        '''
        Returns if the time step is still active
        @param nextStates: data of the nextStates
        @param timeSteps: number of time steps
        @return: True if the timestep if still active, False otherwise
        '''
        return (timeSteps < self._numTimeSteps)

    def toReserve(self):
        '''
        Get the number of timesteps to reserve
        @return: Number of timesteps to reserve
        '''
        return self.getNumTimeSteps()
