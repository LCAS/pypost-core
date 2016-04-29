from rlt.data.DataPreprocessor import DataPreprocessor


class Learner(DataPreprocessor):
    '''
    The Learner class serves as a base class for all learners and predefines
    all necessary methods.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.dataPreprocessors = []
        self.dataNameLearner = 'data'
        self.iteration = 0

        DataPreprocessor.__init__(self)

    def setDataNameLearner(self, dataName):
        self.dataNameLearner = dataName

    def addedData(self, data, newSampleIndices):
        raise NotImplementedError("Not implemented")

    def deletedData(self, data, keepIndices):
        raise NotImplementedError("Not implemented")

    def updateModel(self, data):
        raise NotImplementedError("Not implemented")

    def updateModelCollection(self, dataCollection):
        self.preprocessData(dataCollection)
        self.updateModel(
            dataCollection.getDataObjectForName(
                self.dataNameLearner))

    def printMessage(self, data):
        raise NotImplementedError("Not implemented")

    def addDefaultCriteria(self, trial, evaluationCriterium):
        raise NotImplementedError("Not implemented")

    def preprocessDataCollection(self, dataCollection):
        for preprocessor in self.dataPreprocessors:
            preprocessor.setIteration(self.iteration)
            preprocessor.preprocessDataCollection(dataCollection)

    def addDataPreprocessor(self, dataPreprocessor):
        self.dataPreprocessors.append(dataPreprocessor)
