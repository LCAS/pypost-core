'''
Created on 21.11.2015

@author: Moritz
'''
from interfaces.DataManipulatorInterface import DataManipulatorInterface


class SamplerInterface(DataManipulatorInterface):
    '''
    The SamplerInterface
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()

    def getSamplerName(self):
        '''
        Get the sampler name
        '''
        raise NotImplementedError("Not implemented")

    def _setSamplerName(self, samplerName):
        '''
        Set the sampler name
        '''
        raise NotImplementedError("Not implemented")

    def setSamplerIteration(self, iteration):
        '''
        Set the iteration index
        '''
        raise NotImplementedError("Not implemented")
        # ASK what is the use of this?

    def appendNewSamples(self):
        '''
        Sets the append attribute to true
        '''
        raise NotImplementedError("Not implemented")

    def createSamples(self, newData, *args):
        '''
        Create samples from data and additional arguments
        '''
        raise NotImplementedError("Not implemented")
