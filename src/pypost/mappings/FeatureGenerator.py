from pypost.mappings.Mapping import Mapping
import numpy as np

class FeatureGenerator(Mapping):

    def __init__(self, dataManager, featureMapping):
        Mapping.__init__(self, dataManager, featureMapping.getInputVariables(), featureMapping.getOutputVariables())
        self.featureMapping = featureMapping

        self.dataFunctionDecorator.takesNumElements = featureMapping.isTakesNumElements()
        self.dataFunctionDecorator.takesData = featureMapping.isTakesData()
        self.dataFunctionDecorator.callType = featureMapping.getCallType()

        outputVariables = featureMapping.getOutputVariables()
        self.dataFunctionDecorator.inputArguments = self.dataFunctionDecorator.inputArguments + self.dataFunctionDecorator.outputArguments
        self.dataFunctionDecorator.inputArguments.append(outputVariables[0] + '_validFlag')
        self.dataFunctionDecorator.outputArguments.append(outputVariables[0] + '_validFlag')

        self.dataManager.addFeatureMapping(self)

    @Mapping.MappingMethod()
    def featureGenerator(self, *args):
        numOutputArguments = len(self.dataFunctionDecorator.outputArguments)
        argsNext = list(args[:numOutputArguments-1])
        validFlag = args[-1]
        outArgOld = list(args[-numOutputArguments:-1])

        for i in range(0,len(argsNext)):
            if isinstance(argsNext[i], np.ndarray):
                argsNext[i] = argsNext[i][~validFlag]

        if (self.isTakesData()):
            argsNext[0] = sum(~ validFlag)

        if (sum(~validFlag) > 0):
            outArgsNew = self.featureMapping(*argsNext)

            if not isinstance(outArgsNew, list):  # pragma: no branch
                outArgsNew = [outArgsNew]

            for i in range(0, len(outArgsNew)):
                outArgOld[i][~validFlag] = outArgsNew[i]

        validFlag[:] = True
        outArgOld.append(validFlag)
        return outArgOld

