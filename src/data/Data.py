'''
Created on 12.11.2015

@author: sebastian


Notes: matlab.getDataEntry('actions', :, 1, -1)
       statt ':' könnte man 0 verwenden
'''

import numpy as np


class Data(object):
    '''
    classdocs
    '''

    def __init__(self, dataManager, dataStructure):
        '''
        Constructor
        '''
        self.dataManger = dataManager
        self.dataStructure = dataStructure

        self.initDataStructureEntries()

    def initDataStructureEntries(self):
        pass

    def getDataEntry(self, path, indices=[]):
        '''
        Returns the data points from the required data entry (or
        alias).
        @param path the path to the requested entry as an array.
                    e.g. ['steps', 'subSteps', 'subActions']
        @param indices the hierarchical indices (depending on the hierarchy, it
                       can have different number of elements) as an array.
                       If this parameter is omitted or the number of indices is
                       less than the depth of the hierarchy (less than the
                       length of the path), all other indices will be treated
                       as "...".
                       indices may also be a number which is equivalent to an
                       array containing only one element
        '''
        if isinstance(indices, int):
            indices = [indices]

        return self.dataStructure.getDataEntry(path, indices)
