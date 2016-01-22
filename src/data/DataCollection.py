'''
Created on 22.01.2016

@author: Moritz
'''


class DataCollection(object):
    '''
    A collection for storing data objects
    '''

    def __init__(self, standartData):
        '''
        Set up a DataCollection with a standard data entry
        '''
        self.dataMap = {}

        self.standardDataName = 'data'

        self.dataMap[self.standardDataName] = standartData

    def setDataObject(self, data, name):
        self.dataMap[name] = data

    def getDataObject(self, name):
        return self.dataMap[name]

    def getStandardData(self):
        return self.getDataObject(self.standardDataName)

    def setStandardData(self, data):
        return self.setDataObject(data, self.standardDataName)

    def setStandardDataName(self, name):
        self.standardDataName = name
