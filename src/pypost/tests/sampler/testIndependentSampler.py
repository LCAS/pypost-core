import unittest
from pypost.tests import DataUtil
from pypost.sampler import IndependentSampler



class testIndependentSampler(unittest.TestCase):


    def setUp(self):
        self.dataManager = DataUtil.createTestManager()
        self.sampler = IndependentSampler(self.dataManager, 'episodes')


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIs(self.sampler.dataManager, self.dataManager)
        self.assertTrue(self.sampler.dataManager.isDataEntry('iterationNumber'))

    def test_setParallelSampling(self):
        self.sampler.setParallelSampling(False)
        self.assertFalse(self.sampler.getParallelSampling())

    def test_createSamples(self):
        data = self.dataManager.createDataObject(3)
        self.sampler.createSamples(data)

    def test_isValidEpisode(self):
        self.assertTrue(self.sampler.isValidEpisode())

    def test_getNumSamples(self):
        data = self.dataManager.createDataObject(2)
        self.assertEqual(self.sampler.getNumSamples(data), 10)
        self.sampler._numInitialSamples = 2
        self.assertEqual(self.sampler.getNumSamples(data), 2)

        self.sampler.numSamples = None


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
