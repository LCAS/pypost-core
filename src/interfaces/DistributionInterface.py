'''
Created on 09.01.2016

@author: Moritz
'''

# FIXME why is this needed?
from interfaces.MappingInterface import MappingInterface


class DistributionInterface(MappingInterface):
    '''
    Distribution Interface

    #FIXME this is an interface. move the mathlab reference code from this file to a Distribution base class
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()

        self.dataProbabilityEntries = []

    def setDataProbabilityEntries(self):
        '''
        This function will create a new ProbabilityEntries to the
        dataProbabilityEntries list. The DataEntry will be a combined
        "logQ" + <uppercase first letter output> + <lowercase first letter input>
        The list of data probability entries can be registered via
        registerProbabilityNames()
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
        @return: log likelihood of in- and output data to be related
        '''
        raise NotImplementedError("Not implemented")
