'''
Created on 22.01.2016

@author: Moritz
'''

from dataPreprocessor.DataPreprocessor import DataPreprocessor


class Learner(DataPreprocessor, object):
    '''
    Base class for all learners
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.dataPreprocessors = []
        self.featureGeneratorLearners = []

        self.dataNameLearner = 'data'

        self.iteration = 0

        DataPreprocessor.__init__(self)

    def setDataNameLearner(self, dataName):
        self.dataNameLearner = dataName

    def addedData(self, data, newSampleIndices):
        raise RuntimeError("Not implemented")

    def deletedData(self, data, keepIndices):
        raise RuntimeError("Not implemented")

    def updateModel(self, data):
        raise RuntimeError("Not implemented")

    def updateModelCollection(self, dataCollection):
        self.preprocessData(dataCollection)
        self.updateModel(
            dataCollection.getDataObjectForName(
                self.dataNameLearner))

    def printMessage(self, data):
        raise RuntimeError("Not implemented")

    def addDefaultCriteria(self, trial, evaluationCriterium):
        raise RuntimeError("Not implemented")

    def preprocessDataCollection(self, dataCollection):
        for preprocessor in self.dataPreprocessors:
            preprocessor.setIteration(self.iteration)
            preprocessor.preprocessDataCollection(dataCollection)

    def addDataPreprocessor(self, dataPreprocessor):
        self.dataPreprocessors.append(dataPreprocessor)

    def learnFeatureGenerators(self, data):
        for featureGeneratorLearner in self.featureGeneratorLearners:
            featureGeneratorLearner.updateModel(data)

    def addFeatureGeneratorLearner(self, featureGeneratorLearner):
        self.featureGeneratorLearners.append(featureGeneratorLearner)