'''
Created on Dec 4, 2015

@author: Sebastian Kreutzer
'''

from pypost.data import DataManager

def createTestManager():
    dataManager = DataManager('episodes')
    subDataManager = DataManager('steps')
    subSubDataManager = DataManager('subSteps')

    dataManager.subDataManager = subDataManager
    subDataManager.subDataManager = subSubDataManager

    dataManager.addDataEntry('parameters', 5, -100, 100)
    dataManager.addDataEntry('contexts', 1, -100, 100)
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
    dataManager.addDataEntry('returns', 2, -100, 100)
    subDataManager.addDataEntry('states', 1, -100, 100)
    subDataManager.addDataEntry('actions', 2)
    subSubDataManager.addDataEntry('subStates', 1)
    subSubDataManager.addDataEntry('subActions', 2)
    return dataManager

def createTestManagerSteps():
    dataManager = DataManager('episodes')
    dataManager.addDataEntry('contexts', 2)
    subDataManager = DataManager('steps', isTimeSeries=True)

    dataManager.subDataManager = subDataManager

    subDataManager.addDataEntry('states', 1, -100, 100)
    subDataManager.addDataEntry('actions', 1)
    subDataManager.addDataEntry('rewards', 1)

    return dataManager