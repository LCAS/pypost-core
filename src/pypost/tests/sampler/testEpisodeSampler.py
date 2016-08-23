import unittest

import numpy as np

import pypost.tests.DataUtil as DataUtil
from pypost.data.DataManager import DataManager
from pypost.data.DataManipulator import DataManipulator
from pypost.mappings.Function import Function
from pypost.mappings.FunctionLinearInFeatures import FunctionLinearInFeatures
from pypost.sampler.EpisodeSampler import EpisodeSampler


class SamplerTestManipulator(DataManipulator):
    def __init__(self, dataManager):
        DataManipulator.__init__(self, dataManager)

    @DataManipulator.DataMethod([], ['contexts'])
    def sampleContexts(self, numElements):
        return np.ones((numElements, self.dataManager.getNumDimensions('contexts')))

    @DataManipulator.DataMethod(['contexts'], ['parameters'])
    def sampleParameters(self, contexts):
        return np.ones((contexts.shape[0], self.dataManager.getNumDimensions('contexts'))) + contexts


    @DataManipulator.DataMethod(['contexts', 'parameters'], ['returns'])
    def sampleReturns(self, contexts, parameters):
        temp = np.sum(contexts + parameters, 1)
        temp.resize(contexts.shape[0], 1)
        return temp


class Test(unittest.TestCase):


    def setUp(self):
        self.sampler = EpisodeSampler()
        self.dataManager = self.sampler.getEpisodeDataManager()

        self.dataManager.addDataEntry('contexts', 2)
        self.dataManager.addDataEntry('parameters', 2)
        self.dataManager.addDataEntry('returns', 1)

    def tearDown(self):
        pass

    def testSampling(self):

        testManipulator = SamplerTestManipulator(self.dataManager)

        function = FunctionLinearInFeatures(self.dataManager, [], ['contexts'], 'dummyFunction')
        function.setBias(np.array([1, 1]))
        self.sampler.setContextSampler(function)
        self.sampler.setParameterPolicy(testManipulator.sampleParameters)
        self.sampler.setReturnFunction(testManipulator.sampleReturns)

        data = self.dataManager.getDataObject(10)
        self.sampler.numSamples = 10
        data >> self.sampler

        self.assertTrue((data.getDataEntry('contexts') == np.ones((10,2))).all())
        self.assertTrue((data.getDataEntry('parameters') ==  np.ones((10, 2)) * 2).all())
        self.assertTrue((data.getDataEntry('returns') == np.ones((10, 1)) * 6).all())



    def test_init(self):
        self.assertIsInstance(self.sampler, EpisodeSampler)
        self.assertEqual(self.sampler._samplerName, 'episodes')
        self.assertEqual(self.sampler.dataManager.name, 'episodes')
        self.assertIsNotNone(self.sampler.getSamplerPool('InitEpisode'))
        self.assertIsNotNone(self.sampler.getSamplerPool('ParameterPolicy'))
        self.assertIsNotNone(self.sampler.getSamplerPool('Episodes'))
        self.assertIsNotNone(self.sampler.getSamplerPool('Return'))

    def test_getEpisodeDataManager(self):
        self.assertIsInstance(self.sampler.getEpisodeDataManager(), DataManager)

    def test_setReturnFunction(self):
        dataManager = DataManager('TestmngrH')
        function = Function(dataManager, [], [])
        self.sampler.setReturnFunction(function)

    def test_setParameterPolicy(self):
        datamngr = DataUtil.createTestManager()
        function = Function(datamngr, [], [])
        self.sampler.setParameterPolicy(function)

    def test_setContextSampler(self):
        datamngr = DataUtil.createTestManager()
        function = Function(datamngr, [], [])
        self.sampler.setContextSampler(function)

    def test_flushReturnFunction(self):
        self.test_setReturnFunction()
        self.sampler.flushReturnFunction()
        self.assertListEqual(self.sampler.getSamplerPool("Return").samplerList, [])

    def test_flushParameterPolicy(self):
        self.test_setParameterPolicy()
        self.sampler.flushParameterPolicy()
        self.assertListEqual(self.sampler.getSamplerPool("ParameterPolicy").samplerList, [])

    def test_flushContextSampler(self):
        self.test_setParameterPolicy()
        self.sampler.flushContextSampler()
        self.assertListEqual(self.sampler.getSamplerPool("InitEpisode").samplerList, [])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
