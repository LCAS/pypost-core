import unittest
import rlt.tests.DataUtil
import numpy as np
from rlt.data.Data import Data
from rlt.data.DataStructure import DataStructure
from rlt.data.DataManager import DataManager
from rlt.sampler.SequentialResetSampler import SequentialResetSampler
from rlt.sampler.Sampler import Sampler

class TestSequentialResetSampler(SequentialResetSampler):

    def _toReserve(self):
        return 3

    def _initSamples(self, data, indexing):
        parameterData = np.ones((3, 5))
        data.setDataEntry('parameters', [], parameterData)

    def _createSamplesForStep(self, data, indexing):
        indexing[0].pop()
        return indexing

    def _endTransition(self, data, indexing):
        pass

    def _adjustReservedStorage(self, data, indexing):
        parameterData = np.full((6, 2), indexing[-1])
        data.setDataEntry('context', [], parameterData)

class TestSequentialResetSampler2(SequentialResetSampler):
    def __init__(self, dataManager, samplerName):
        pass

class testSequentialResetSampler(unittest.TestCase):


    def setUp(self):
        dataManager = DataUtil.createTestManager()
        self.sampler = TestSequentialResetSampler(dataManager, 'testSampler')
        self.sampler2 = TestSequentialResetSampler2(DataManager('testmngr'), 'testSampler2')

    def tearDown(self):
        pass

    def test_init(self):
        self.assertIsInstance(self.sampler, SequentialResetSampler)
        self.assertIsInstance(self.sampler2, SequentialResetSampler)
        self.assertEqual(self.sampler._numSamples, 3)

    def test_createSamples(self):
        datamngr = DataUtil.createTestManager()
        data = datamngr.getDataObject(3)
        self.sampler.createSamples(data, [10, 4, 3, 11])

        testRetArr = np.ones((3, 5))
        testRetArr = np.vstack((testRetArr, np.zeros((3, 5))))
        self.assertTrue((data.getDataEntry('parameters', ...) == testRetArr).all())
        self.assertTrue((data.getDataEntry('context', ...) == np.full((6, 2), 4)).all())

    def test_getNumSamples(self):
        self.sampler.numTimeSteps = 7
        self.assertEqual(self.sampler.getNumSamples(None, None), 7)

    def test_toReserve(self):
        with self.assertRaises(NotImplementedError):
            self.sampler2._toReserve()

    def test_endTransition(self):
        with self.assertRaises(NotImplementedError):
            self.sampler2._endTransition(None, None)

    def test_initSamples(self):
        with self.assertRaises(NotImplementedError):
            self.sampler2._initSamples(None, None)

    def test_createSamplesForStep(self):
        with self.assertRaises(NotImplementedError):
            self.sampler2._createSamplesForStep(None, None)

    def test_adjustReservedStorage(self):
        with self.assertRaises(NotImplementedError):
            self.sampler2._adjustReservedStorage(None, None)

    def test_selectActiveIdxs(self):
        with self.assertRaises(NotImplementedError):
            self.sampler2._selectActiveIdxs(None, None)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
