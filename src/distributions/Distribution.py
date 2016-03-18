from distributions.DistributionInterface import DistributionInterface


class Distribution(DistributionInterface):
    '''
    classdocs
    '''

    def __init__(self, dataManager):
        '''
        Constructor

        :change: dataManager was removed from function arguments and is now a constructor argument.
        '''
        DistributionInterface.__init__(self)

        self.dataManager = dataManager
        '''
        The data manager to register the distribution to
        '''

        self.dataProbabilityEntries = []
        '''
        The distribution entries to register
        '''

    def setDataProbabilityEntries(self):
        # FIXME we left this unimplemented because we didn't see a real use case
        # this function
        raise NotImplementedError("Not implemented")

    def registerProbabilityNames(self, layerName):
        '''
        registers all data probability entries on the dataProbabilityEntries
        list
        '''
        for i in range(len(self.dataProbabilityEntries)):
            self.dataManager.addDataEntry(
                [layerName + "." + self.dataProbabilityEntries[i]], 1)

    def getDataProbabilityNames(self, dataManager, layerName):
        '''
        FIXME we left this unimplemented because we didn't see a real use case
        '''
        raise NotImplementedError("Not implemented")

    def _registerMappingInterfaceDistribution(self):
        '''
        registers a mapping and data function
        :change
        '''
        raise NotImplementedError("Not implemented")

    def sampleFromDistribution(self, numElements):
        '''
        get a matrix of with numElements many samples from this distribution
        #TODO there where varargs, check if the are really needed
        '''
        raise NotImplementedError("Not implemented")

    def getDataProbabilities(self, inputData, outputData):
        '''
        get the log likelihood for a given set of in- and output data to be related
        #TODO there where varargs, check if the are really needed
        :returns: log likelihood of in- and output data to be related
        '''
        raise NotImplementedError("Not implemented")
