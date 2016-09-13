import unittest
from pypost.tests import DataUtil
from pypost.sampler import SequentialSampler, SamplerPool

class testSequentialSampler(unittest.TestCase):


    def setUp(self):
        self.sampler = SequentialSampler(DataUtil.createTestManager(), 'episodes', 'steps')
        self.sampler.addSamplerPool(SamplerPool('testPool1', 0))
        self.sampler.addSamplerPool(SamplerPool('testPool2', 7))
        self.sampler.addSamplerPool(SamplerPool('testPool3', 2))
        self.sampler.addSamplerPool(SamplerPool('testPool4', 11))
        self.sampler2 = SequentialSampler(DataUtil.createTestManager(), 'episodes', 'steps')
        self.sampler2.addSamplerPool(SamplerPool('testPool5', 9))


    def tearDown(self):
        pass

    def test_init(self):
        pass


    def test_setIsActiveSampler(self):
        pass #TODO


    def test_createSamples(self): #TODO
        data = DataUtil.createTestManager().getDataObject(1)
        self.assertRaises(NotImplementedError, self.sampler.createSamples, data)

    def test_getNumSamples(self):
        pass

    def test_selectActiveIdxs(self):
        pass

    def test_endTransitation(self):
        pass

    def test_initSamples(self):
        with self.assertRaises(NotImplementedError):
            self.sampler._initSamples(None)

    def test_createSamplesForStep(self):
        with self.assertRaises(NotImplementedError):
            self.sampler._createSamplesForStep(None)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
