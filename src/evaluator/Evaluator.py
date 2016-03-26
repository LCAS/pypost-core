'''
Created on Dec 13, 2015

@author: moritz
'''
from evaluator.LogType import LogType
from experiments.Trial import StoringType

class Evaluator():
    '''
    Base evaluator class

    Methods (annotated):
    def __init__(self, name: str, hook: Set of str, storingType: experiments.Trial.Storingtype) -> None
    def publish(self, string: str, logType: evaluator.LogType =None) -> None
    '''


    def __init__(self, name, hook, storingType):
        ''' Constructor

        :param name: Name of the evaluator
        :param hook: Array of iterations
        :param storingType: Type of storage

        TODO seems like every evaluator uses the endLoop hook, maybe hard-code it?
        '''

        self.name=name
        '''
        Name of the evaluator
        '''

        self.hook=hook
        '''
        array of iterations to execute the evaluator
        '''

        self.storingType=storingType
        '''
        the storing type as an Enum
        '''

    def publish(self, string, logType=None):
        ''' Prints the given message for the Evaluator

        :param string: The message to be printed
        :param logType: The type of this message (EVALUATION, WARNING, ERROR)
        '''
        if logType==None:
            logType=LogType.EVALUATION

        #FIXME add filters for different log types
        print(self.name+': '+string)

    def getEvaluation(self, data, newData, trial):
        '''
        Evaluate the given data
        '''
        raise NotImplementedError("Not implemented")
