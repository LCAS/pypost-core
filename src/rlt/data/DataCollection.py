class DataCollection():
    '''
    A collection for storing data objects
    '''

    def __init__(self, standartData=None):
        '''
        Set up a DataCollection with a default data entry

        :param standartData: the data object to store as default data
        '''
        self.dataMap = {}

        self._standardDataName = 'data'

        self.dataMap[self._standardDataName] = standartData

    def setDataObject(self, data, name):
        if name == "":
            raise RuntimeError("data object name can not be empty");
        self.dataMap[name] = data

    def getDataObject(self, name):
        return self.dataMap[name]

    def getStandardData(self):
        return self.getDataObject(self._standardDataName)

    def setStandardData(self, data):
        return self.setDataObject(data, self._standardDataName)

    def getStandardDataName(self):
        return self._standardDataName

    def setStandardDataName(self, name):
        if name=="":
            raise RuntimeError("standard data name can not be empty");
        self._standardDataName = name
