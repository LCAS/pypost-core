from functions.MappingInterface import MappingInterface


class DistributionInterface(MappingInterface):
    '''
    Distribution Interface
    '''

    def __init__(self):
        '''
        Constructor
        '''
        MappingInterface.__init__(self)

    def setDataProbabilityEntries(self):
        '''
        This function will create a new ProbabilityEntries to the
        dataProbabilityEntries list. The Dataentry will be a combined
        string `'logQ' + <uppercase of the first letter of the output
        variable> + <lowercase of the first letter of the input variable>`.
        The list of data probability entries can be registered via
        `:func:registerProbabilityNames()`.
        '''
        raise NotImplementedError("Not implemented")

    def registerProbabilityNames(self, dataManager, layerName):
        '''
        registers all data probability entries on the dataProbabilityEntries
        list, created via setDataProbabilityEntries()
        '''
        raise NotImplementedError("Not implemented")

    def getDataProbabilityNames(self, dataManager, layerName):
        '''
        get all the probability entry names
        '''
        raise NotImplementedError("Not implemented")

    def _registerMappingInterfaceDistribution(self):
        '''
        registers a mapping and data function
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
