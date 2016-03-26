from distributions.DistributionInterface import DistributionInterface
from functions.Mapping import Mapping


class Distribution(DistributionInterface, Mapping):
    '''
    classdocs
    '''

    def __init__(self, dataManager):
        '''
        Constructor

        :change: dataManager was removed from function arguments and is now a constructor argument.
        '''
        DistributionInterface.__init__(self)
        Mapping.__init__(self, dataManager)

        self.dataProbabilityEntries = []
        '''
        The distribution entries to register
        '''

    def setDataProbabilityEntries(self):
        '''
        This function will create a new ProbabilityEntries to the
        dataProbabilityEntries list. The DataEntry will be a combined
        string <tt>'logQ' + <uppercase of the first letter of the output
        variable>+<lowercase of the first letter of the input variable></tt>.
        The list of data probability entries can be registered via
        <tt>registerProbabilityNames()</tt>.
        '''
        inputVariablesShort = ""
        outputVariablesShort = ""

        # concatenate the first letter of all input vars
        for inputVar in self.inputVariables:
            inputVariablesShort = inputVariablesShort + inputVar[0].lower()

        for outputVar in self.outputVariables:
            outputVariablesShort = outputVariablesShort + outputVar[0].upper()

        self.dataProbabilityEntries.append(
            'logQ' +
            outputVariablesShort +
            inputVariablesShort)

    def registerProbabilityNames(self, layerName):
        '''
        registers all data probability entries on the dataProbabilityEntries
        list
        '''
        for dataProbabilityEntry in self.dataProbabilityEntries:
            self.dataManager.addDataEntry(
                layerName +
                "." +
                dataProbabilityEntry,
                1)

    def getDataProbabilityNames(self):
        return list(self.dataProbabilityEntries)

    def _registerMappingInterfaceDistribution(self):
        '''
        registers a mapping and data function
        #FIXME it seems like registerDataFunctions is never set to true ^moritz
        '''
        if self.registerDataFunctions:
            self.addMappingFunction("sampleFromDistribution")

            if not self.outputVariables:
                self.setDataProbabilityEntries()
                self.addDataManipulationFunction(
                    self.getDataProbabilities,
                    self.inputVariables + self.outputVariables,
                    self.dataProbabilityEntries)

    def sampleFromDistribution(self, numElements, *args):
        '''
        get a matrix of with numElements many samples from this distribution
        :param numElements
        :param varargin:    parameter for the abstract `getExpectationAndSigma()`
                            function. Parameters depend on the subclass you are using.
        :return             a number of random samples of the distribution
        :abstract
        '''
        raise NotImplementedError("Not implemented")

    def getDataProbabilities(self, inputData, outputData):
        '''
        get the log likelihood for a given set of in- and output data to be related in this distribution
        #TODO there where varargs, check if the are really needed
        :returns: log likelihood of in- and output data to be related
        :abstract
        '''
        raise NotImplementedError("Not implemented")
