from pypost.data.DataManipulator import DataManipulator


class SamplerInterface(DataManipulator):
    '''
    The SamplerInterface
    '''

    def __init__(self, dataManager, samplerName):
        '''
        Constructor
        '''
        DataManipulator.__init__(self, dataManager)

        self.dataManager = dataManager
        '''
        The data manager responsible for this sampler
        '''
        self._samplerName = samplerName
        '''
        String of the sampler name
        :change: now holds samplerPool instances instead of their names
        '''

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
