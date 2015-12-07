'''
Created on Dec 4, 2015

@author: Sebastian Kreutzer
'''

from DataManager import DataManager
from Data import Data


def createTestManager():
    dataManager = DataManager('episodes')
    subDataManager = DataManager('steps')
    subSubDataManager = DataManager('subSteps')

    dataManager.subDataManager = subDataManager
    subDataManager.subDataManager = subSubDataManager

    dataManager.addDataEntry('parameters', 5)
    dataManager.addDataEntry('context', 2)
    subDataManager.addDataEntry('states', 1)
    subDataManager.addDataEntry('actions', 2)
    subSubDataManager.addDataEntry('subStates', 1)
    subSubDataManager.addDataEntry('subActions', 2)
    return dataManager
