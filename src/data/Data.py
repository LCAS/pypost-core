'''
Created on 12.11.2015

@author: sebastian
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