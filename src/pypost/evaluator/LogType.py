'''
Created on Dec 13, 2015

@author: moritz
'''

from enum import Enum

class LogType(Enum):
    '''
    Enumeration value for output data type
    '''
    EVALUATION = 0
    WARNING = 1
    ERROR = 2