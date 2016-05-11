import unittest
import time
import csv
import sys
import os
import numpy as np
from numpy import ones

from pypost.data.DataEntry import DataEntry
from pypost.data.DataManager import DataManager
from pypost.data.DataManipulator import DataManipulator
from pypost.data.DataManipulator import CallType
from pypost.experiments.ExperimentFromScript import ExperimentFromScript
from pypost.experiments.Experiment import Experiment
from pypost.examples.stochasticSearch.rosenbrock.Power_Rosenbrock import PowerRosenbrock

class TestManipulator(DataManipulator):
    def __init__(self, dataManager):
        super().__init__(dataManager)
        self.addDataManipulationFunction(self.sampleParameters, [],
                                         ['parameters'])
        self.addDataManipulationFunction(self.sampleStates, ['parameters'],
                                         'states', CallType.PER_EPISODE, True)
        self.addDataManipulationFunction(self.sampleActions, ['parameters', 'states'],
                                         ['actions'], CallType.PER_EPISODE, True)

    def sampleParameters(self, numElements):
        return np.ones((numElements, 10))

    def sampleStates(self, numElements, parameters):
        return np.ones((numElements, 2))

    def sampleActions(self, numElements, parameters, states):
        #return np.ones((numElements, 2))
        return states - parameters[:, 0:1]

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

    def registerTime(self, testName):
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
        self.registerTime('getDataObject')

        self.start()
        myData.reserveStorage([100, 20, 5])
        self.stop()
        self.registerTime('reserveStorage')

        actions = np.random.random((2000, 2))
        subActions = np.random.random((5000, 2))

        self.start()
        myData.setDataEntry('actions', [..., ...], actions)
        self.stop()
        self.registerTime('setDataEntry1')

        self.start()
        myData.setDataEntry('subActions', [..., ..., ...], subActions)
        self.stop()
        self.registerTime('setDataEntry2')

        self.start()
        myData.getDataEntry('subActions')
        self.stop()
        self.registerTime('getDataEntry')

        self.start()
        for i in range(0, 100):
            entryList = myData.getDataEntryList([['steps', 'actions'], ['steps', 'substeps', 'subActions']], [0, 1, 0])
        self.stop()
        self.registerTime('getDataEntryCellArray')

        entryList[1] = 2 * entryList[1]
        self.start()
        for i in range(0, 100):
            myData.setDataEntryList([['steps', 'actions'], ['steps', 'substeps', 'subActions']], [0, 1, 0], entryList)
        self.stop()
        self.registerTime('setDataEntryCellArray')


    def test_DataManipulator(self):
        dataManager = DataManager("episodes")
        subDataManager = DataManager("steps")

        dataManager.addDataEntry('parameters', 10, -ones(5), ones(5))

        subDataManager.addDataEntry('states', 2, -ones(1), ones(1))
        subDataManager.addDataEntry('actions', 2, -ones(2), ones(2))

        dataManager.subDataManager = subDataManager

        data = dataManager.getDataObject([10, 10])

        manipulator = TestManipulator(dataManager)

        self.start()
        for i in range(0, 1000):
            manipulator.callDataFunction('sampleParameters', data)
        self.stop()
        self.registerTime('callDataFunction')

        self.start()
        for i in range(0, 100):
            manipulator.callDataFunctionOutput('sampleActions', data)
        self.stop()
        self.registerTime('callDataFunctionOuput')

    def test_Experiment(self):
        if not os.path.isdir('/tmp/testCategory'):
            os.mkdir('/tmp/testCategory')
        if not os.path.isdir('/tmp/testCategory/PowerRosenbrock'):
            os.mkdir('/tmp/testCategory/PowerRosenbrock')

        self.start()
        experiment = ExperimentFromScript('/tmp', 'testCategory', PowerRosenbrock)
        experiment.create()
        evaluation = experiment.addEvaluation(['maxSizeReferenceStat'], [300], 100)
        self.stop()
        self.registerTime('createExperiment')

        self.start()
        experiment.startLocal()
        self.stop()
        self.registerTime('runExperiment')

if __name__ == '__main__':
    unittest.main()
