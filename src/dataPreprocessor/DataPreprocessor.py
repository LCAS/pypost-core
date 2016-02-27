class DataPreprocessor(object):
    '''
    Base class for Data Preprocessors
    '''

    def __init__(self, name=None):
        '''
        Set up the data preprocessor
        '''

        self.iteration = 0

        self.name = "DataPreprocessor"

        if name is not None:
            if name == "":
                raise RuntimeError("name can not be empty")
            self.name = name

    def preprocessData(self, data):
        '''
        takes the given data and returns the preprocessed result
        :param data: data to process
        '''
        raise NotImplementedError("Not implemented")

    def preprocessDataCollection(self, dataCollection):
        '''
        Preprocess a collection of data and store the new data back into the collection
        :param dataCollection: the data collection to process
        '''
        newData = self.preprocessData(dataCollection.getStandardData())
        dataCollection.addDataObject(newData, self.name)

    def setIteration(self, iteration):
        if (iteration<0):
            raise RuntimeError("Iteration value can not be negative")

        self.iteration = iteration
