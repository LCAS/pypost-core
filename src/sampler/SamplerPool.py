'''
Created on 21.11.2015

@author: Moritz
'''

class SamplerPool(object):
    '''
    A collection of samplers
    '''

    def __init__(self,name,priority):
        '''
        Creates a sampler pool with an empty sampler list
        '''
        self.samplerList=[]
        self.setName(name)
        self.setPriority(priority)
    
    #getters & setters
    
    def getName(self):
        return self._name
    
    def _setName(self, name):
        self._name=name
    
    def getPriority(self):
        return self._priority
    
     
    def _setPriority(self, priority):
        '''
        @change: only positive priorities are allowed [0,...] 
        '''
        if priority<0:
            raise RuntimeError("Priority has to be greater or equal to zero")
        self._priority=priority
    
    def flush(self):
        '''
        Clear all samplers in this pool
        '''
        self.samplerList.clear(); 