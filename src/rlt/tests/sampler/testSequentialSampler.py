import unittest
import rlt.tests.DataUtil
from rlt.sampler.SequentialSampler import SequentialSampler
from rlt.data.Data import Data
from rlt.data.DataStructure import DataStructure
from rlt.sampler.SamplerPool import SamplerPool
from rlt.data.DataManager import DataManager


class testSequentialSampler(unittest.TestCase):


    def setUp(self):
        self.sampler = SequentialSampler(DataUtil.createTestManager(), 'testSampler1', None)
        self.sampler.addSamplerPool(SamplerPool('testPool1', 0))
        self.sampler.addSamplerPool(SamplerPool('testPool2', 7))
        self.sampler.addSamplerPool(SamplerPool('testPool3', 2))
        self.sampler.addSamplerPool(SamplerPool('testPool4', 11))
        self.sampler2 = SequentialSampler(DataManager('testDataManager2'), 'testSampler2', 'mySteps')
        self.sampler2.addSamplerPool(SamplerPool('testPool5', 9))
        self.sampler.addLowLevelSampler('testPool1', self.sampler2, False)


    def tearDown(self):
        pass

    def test_init(self):
        pass


    def test_setIsActiveSampler(self):
        pass #TODO

    def test_addElementsForTransition(self):
        self.sampler.addElementsForTransition('elemName', 'newElemName')

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
