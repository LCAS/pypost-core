'''
Created on Dec 4, 2015

@author: Sebastian Kreutzer
'''

from data.DataManager import DataManager
from data.Data import Data


def createTestManager():
    dataManager = DataManager('episodes')
    subDataManager = DataManager('steps')
    subSubDataManager = DataManager('subSteps')

    dataManager.subDataManager = subDataManager
    subDataManager.subDataManager = subSubDataManager

    dataManager.addDataEntry('parameters', 5, -100, 100)
    dataManager.addDataEntry('context', 2, -100, 100)
    subDataManager.addDataEntry('states', 1, -100, 100)
    subDataManager.addDataEntry('actions', 2)
    subSubDataManager.addDataEntry('subStates', 1)
    subSubDataManager.addDataEntry('subActions', 2)
    return dataManager


def createTestManager2():
    dataManager = DataManager('episodes2')
    subDataManager = DataManager('steps2')
    subSubDataManager = DataManager('subSteps2')

    dataManager.subDataManager = subDataManager
    subDataManager.subDataManager = subSubDataManager

    dataManager.addDataEntry('parameters', 5, -100, 100)
    dataManager.addDataEntry('context', 4, -100, 100)
    dataManager.addDataEntry('goals', 8, -100, 100)
    subDataManager.addDataEntry('states', 1, -100, 100)
    subDataManager.addDataEntry('actions', 2)
    subSubDataManager.addDataEntry('subStates', 1)
    subSubDataManager.addDataEntry('subActions', 2)
    return dataManager