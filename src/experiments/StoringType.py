'''
Created on Dec 13, 2015

@author: moritz
'''

from enum import Enum

class StoringType(Enum):
    '''
    Enumeration value for experiment data storage
    '''
    NONE = 0
    STORE = 1
    ACCUMULATE = 2
    STORE_PER_ITERATION = 3
    ACCUMULATE_PER_ITERATION = 4