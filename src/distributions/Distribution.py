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
        self.registerDataFunctions = True
        '''
        Whether or not to register a data function for this distribution
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

        name = 'logQ' + outputVariablesShort + inputVariablesShort

        # short name is always registered at index 0
        if not self.dataProbabilityEntries:
            self.dataProbabilityEntries.append(name)
        else:
            self.dataProbabilityEntries[0] = name

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
        Registers a mapping and data function.
        Use the registerDataFunctions switch to turn function registration off
        '''
        if self.registerDataFunctions:
            self.addMappingFunction(self.sampleFromDistribution)
            if len(self.outputVariables) != 0:
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
        :returns: log likelihood of in- and output data to be related
        :abstract
        '''
        raise NotImplementedError("Not implemented")
