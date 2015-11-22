'''
Created on 21.11.2015

@author: Moritz
'''


class SamplerInterface(object, DataManipulatorInterface):
    '''
    The SamplerInterface
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super(DataManipulatorInterface, self).__init__()

    def setSamplerIteration(self, iteration):
        raise NotImplementedError("Not implemented")

    def appendNewSamples(self):
        raise NotImplementedError("Not implemented")

    def createSamples(self, newData, *args):
        raise NotImplementedError("Not implemented")
