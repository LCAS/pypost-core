import unittest
import DataUtil
from sampler.SequentialSampler import SequentialSampler
from data.Data import Data
from data.DataStructure import DataStructure


class Test(unittest.TestCase):


    def setUp(self):
        self.sampler = SequentialSampler(DataUtil.createTestManager(), 'testSampler1')
        self.sampler.addSamplerPool(SamplerPool('testPool1', 0))
        self.sampler.addSamplerPool(SamplerPool('testPool2', 7))
        self.sampler.addSamplerPool(SamplerPool('testPool3', 2))
        self.sampler.addSamplerPool(SamplerPool('testPool4', 11))
        self.sampler2 = SequentialSampler(DataManager('testDataManager2'), 'testSampler2')
        self.sampler2.addSamplerPool(SamplerPool('testPool5', 9))
        self.sampler.addLowerLevelSampler('testPool1', sampler2, False)


    def tearDown(self):
        pass

    def test_init(self):
        pass


    def test_setIsActiveSampler(self):
        pass #TODO

    def test_addElementsForTransition(self):
        self.sampler.addElementsForTransition('elemName', 'newElemName')

    def test_createSamples(self): #TODO
        data = Data(DataUtil.createTestManager(), DataStructure(1))
        self.sampler.createSamples(data)

    def test_getNumSamples(self):
        #TODO

    def test_selectActiveIdxs(self):
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()