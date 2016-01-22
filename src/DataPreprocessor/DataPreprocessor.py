'''
Created on 22.01.2016

@author: Moritz
'''


class DataPreprocessor(object):
    '''
    Base class for Data Preprocessors
    '''

    def __init__(self, name=""):
        '''
        Set up the data preprocessor
        '''

        self.iteration = 0

        self.name = ""

        if name != "":
            self.name = name

    def PreprocessData(self, data):
        '''
        takes the given data and returns the preprocessed result
        @param data: data to process
        '''
        raise NotImplementedError("Not implemented")

    def preprocessDataCollection(self, dataCollection):
        '''
        Preprocess a collection of data and store the new data back into the collection
        @param dataCollection: the data collection to process
        '''
        newData = self.PreprocessData(dataCollection.getStandardData())
        dataCollection.addDataObject(newData, self.name)

    def setIteration(self, iteration):
        self.iteration = iteration
