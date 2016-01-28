import unittest
import time
import csv
import sys
import numpy as np
from numpy import ones
sys.path.append('../src')
from data.DataEntry import DataEntry
from data.DataManager import DataManager


class testPerformanceRequirements(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        self.startTime = 0
        self.endTime = 0
        self.performanceTests = {}

        with open('performance_tests.tsv', 'r') as file:
            reader = csv.reader(file, delimiter='\t')
            it = iter(reader)
            next(it)
            for row in it:
                name, domain, description, time = row
                self.performanceTests[name] = {
                    'domain': domain, 'description': description, 'time': float(time)}

        unittest.TestCase.__init__(self, methodName=methodName)
        
    def start(self):
        self.startTime = time.time()
        
    def stop(self):
        self.endTime = time.time()

    def compareToReferenceTime(self, testName):
        delta = self.endTime - self.startTime
        self.assertIn(
            testName, self.performanceTests, "Performance test %s is not defined" % testName)
        referenceTime = self.performanceTests[testName]['time']
        if delta <= referenceTime:
            print("Time requirement for %s met: Expected less than %f, measured %f. Speedup: %f" % (testName, referenceTime, delta, referenceTime / delta))
        else:
            self.fail("Time requirement for %s not met (Expected less than %f, measured %f)" % (testName, referenceTime, delta))

    def test_DataManager(self):
        dataManager = DataManager("episodes")
        subDataManager = DataManager("steps")
        subSubDataManager = DataManager("substeps")

        dataManager.addDataEntry('parameters', 5, -ones(5), ones(5))
        dataManager.addDataEntry('context', 2, -ones(2), ones(2))

        subDataManager.addDataEntry('states', 1, -ones(1), ones(1))
        subDataManager.addDataEntry('actions', 2, -ones(2), ones(2))

        subSubDataManager.addDataEntry('subStates', 1, -ones(1), ones(1))
        subSubDataManager.addDataEntry(
            'subActions', 2, -ones(2), ones(2))

        dataManager.subDataManager = subDataManager
        subDataManager.subDataManager = subSubDataManager

        self.start()
        myData = dataManager.getDataObject([100, 10, 5])
        self.stop()
        self.compareToReferenceTime('getDataObject')
        
        self.start()
        myData.reserveStorage([100, 20, 5])
        self.stop()
        self.compareToReferenceTime('reserveStorage')
        
        actions = np.random.random((2000, 2))
        subActions = np.random.random((5000, 2))
    
        self.start()
        myData.setDataEntry('actions', [..., ...], actions)
        self.stop()
        self.compareToReferenceTime('setDataEntry1')
        
        self.start()
        myData.setDataEntry('subActions', [..., ..., ...], subActions)
        self.stop()
        self.compareToReferenceTime('setDataEntry2')
        
        self.start()
        myData.getDataEntry('subActions')
        self.stop()
        self.compareToReferenceTime('getDataEntry')
   
        self.start()
        for i in range(0, 100):
            entryList = myData.getDataEntryList([['steps', 'actions'], ['steps', 'substeps', 'subActions']], [0, 1, 0])
        self.stop()
        self.compareToReferenceTime('getDataEntryCellArray')

        entryList[1] = 2 * entryList[1]
        self.start()
        for i in range(0, 100):
            myData.setDataEntryList([['steps', 'actions'], ['steps', 'substeps', 'subActions']], [0, 1, 0], entryList)
        self.stop()
        self.compareToReferenceTime('setDataEntryCellArray')
        
if __name__ == '__main__':
    unittest.main()