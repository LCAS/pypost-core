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
        '''
        This function will create a new ProbabilityEntries to the
        dataProbabilityEntries list. The Dataentry will be a combined
        string `'logQ' + <uppercase of the first letter of the output
        variable> + <lowercase of the first letter of the input variable>`.
        The list of data probability entries can be registered via
        `:func:registerProbabilityNames()`.
        '''
        inputVariablesShort = ''
        outputVariablesShort = ''

        for i in range(0, len(self.inputVariables)):
            if isinstance(self.inputVariables[i], list):
                for j in range(0, len(self.inputVariables[i])):
                    inputVariablesShort.append(
                        self.inputVariables[i][j][0].lower())
            else:
                inputVariablesShort += self.inputVariables[i][0].lower()

        outputVariablesShort += self.outputVariable[0].upper()

        if len(self.dataProbabilityEntries) == 0:
            self.dataProbabilityEntries.append(None)

        self.dataProbabilityEntries[0] = 'logQ' + outputVariablesShort + inputVariablesShort

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

    def registerMappingInterfaceDistribution(self):
        '''
        registers a mapping and data function
        :change
        '''
        self.registerDataFunctions=True

        if self.registerDataFunctions:
            self.addMappingFunction(self.sampleFromDistribution)
            if self.outputVariable is not None:
                self.setDataProbabilityEntries()
                if self.registerDataFunctions:
                    if self.inputVariables is None:
                        inputArgsLogLik = [self.inputVariables,
                                           self.outputVariable, self.additionalInputVariables]
                    else:
                        inputArgsLogLik = [self.inputVariables,
                                           self.outputVariable, self.additionalInputVariables]

                    self.addDataManipulationFunction(
                        self.getDataProbabilities, inputArgsLogLik,
                        self.dataProbabilityEntries)

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
