'''
Created on 22.11.2015

@author: Moritz
'''


class DataManipulatorInterface(object):
    '''
    FIXME
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()

    def isSamplerFunction(self, samplerName):
        '''
        FIXME needed by Sampler
        '''
        raise NotImplementedError("Not implemented")

    def callDataFunction(self, samplerName, newData, *args):
        '''
        '''
        raise NotImplementedError("Not implemented")
