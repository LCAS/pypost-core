from pypost.functions.Mapping import Mapping
from pypost.data.DataManipulator import DataManipulator


class Distribution(Mapping):
    '''
    classdocs
    '''

    def __init__(self, dataManager, inputVariables = [], outputVariable = [], name = ""):
        '''
        Constructor

        :change: dataManager was removed from function arguments and is now a constructor argument.
        '''
        Mapping.__init__(self, dataManager, inputVariables, outputVariable, name)


    @Mapping.DataMappingFunction()
    def sampleFromDistribution(self, *args):
        '''
        get a matrix of with numElements many samples from this distribution
        :param numElements
        :param varargin:    parameter for the abstract `getExpectationAndSigma()`
                            function. Parameters depend on the subclass you are using.
        :return             a number of random samples of the distribution
        :abstract
        '''
        raise NotImplementedError("Not implemented")

    @DataManipulator.DataManipulationMethod(inputArguments = ['self.inputVariables', 'self.outputVariables'], outputArguments=[])
    def getDataLogLikelihood(self, inputData, outputData):
        '''
        get the log likelihood for a given set of in- and output data to be related in this distribution
        :returns: log likelihood of in- and output data to be related
        :abstract
        '''
        raise NotImplementedError("Not implemented")
