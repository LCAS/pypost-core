import unittest
import time
import csv
import sys
import numpy as np
from numpy import ones
from numpy.doc import performance
sys.path.append('../src/data')
from DataEntry import DataEntry
from DataManager import DataManager


class testPerformanceRequirements(unittest.TestCase):

    def __init__(self, methodName='runTest'):
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


    def assertFastEnough(self, testName, time):
        self.assertIn(
            testName, self.performanceTests, "Performance test %s is not defined" % testName)
        reference = self.performanceTests[testName]['time']
        self.assertLessEqual(
            time, reference, "Time requirement for %s not met (Expected less than %f, measured %f)" % (testName, reference, time))

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

        start = time.time()
        myData = dataManager.getDataObject([100, 10, 5])
        end = time.time()
        self.assertFastEnough("getDataObject", end - start)
        
        print(end - start)
        
        start = time.time()
        #Data.reserveStorage([100, 20, 5]) # FIXME Not implemented yet
        end = time.time()
        self.assertFastEnough("reserveStorage", end - start)
        
        
