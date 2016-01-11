'''
Created on Dec 13, 2015

@author: moritz
'''
from evaluator.LogType import LogType

class Evaluator(object):
    '''
    Base evaluator class
    '''


    def __init__(self, name, hook, storingType):
        '''
        Constructor
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
        FIXME enum?
        '''
        
    def publish(self, string, logType=None):
        if logType==None:
            logType=LogType.EVALUATION
        
        #FIXME add filters for different log types
        print(self.name+': '+string)
    
    def getEvaluation(self, data, newData, trial):
        '''
        Evaluate the given data
        '''
        raise NotImplementedError("Not implemented")