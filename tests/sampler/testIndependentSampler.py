import unittest
import DataUtil
from sampler.IndependentSampler import IndependentSampler
from data.DataManager import DataManager
from data.Data import Data
from data.DataStructure import DataStructure


class testIndependentSampler(unittest.TestCase):


    def setUp(self):
        self.dataManager = DataUtil.createTestManager()
        self.sampler = IndependentSampler(self.dataManager, 'testSampler1')


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIs(self.sampler.dataManager, self.dataManager)
        self.assertTrue(self.sampler.dataManager.isDataEntry('iterationNumber'))

    def test_setParallelSampling(self):
        self.sampler.setParallelSampling(False)
        self.assertFalse(self.sampler.getParallelSampling())

    def test_createSamples(self):
        data = Data(DataUtil.createTestManager(), DataStructure(3))
        self.sampler.createSamples(data)

        data = Data(DataUtil.createTestManager()), DataStructure(3)
        with self.assertRaises(NotImplementedError):
            self.sampler.createSamples(data, 3)

    def test_isValidEpisode(self):
        self.assertTrue(self.sampler.isValidEpisode())

    def test_getNumSamples(self):
        data = Data(DataUtil.createTestManager(), DataStructure(2))
        self.assertEqual(self.sampler.getNumSamples(data), 0)
        self.sampler._numInitialSamples = 2
        self.assertEqual(self.sampler.getNumSamples(data), 2)

        self.sampler._numSamples = None
        with self.assertRaises(RuntimeError):
            self.sampler.getNumSamples(data)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()