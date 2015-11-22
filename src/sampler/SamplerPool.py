'''
Created on 21.11.2015

@author: Moritz
'''


class SamplerPool(object):
    '''
    A collection of samplers
    '''

    def __init__(self, name, priority):
        '''
        Creates a sampler pool with an empty sampler list
        '''
        self.samplerList = []
        self.setName(name)
        self.setPriority(priority)

    # getters & setters

    def getName(self):
        return self._name

    def _setName(self, name):
        self._name = name

    def getPriority(self):
        return self._priority

    # CHANGE only positive priorities are allowed [0,...]
    def _setPriority(self, priority):
        if priority < 0:
            raise RuntimeError("Priority has to be greater than zero")
        self._priority = priority

    def flush(self):
        self.samplerList.clear()
