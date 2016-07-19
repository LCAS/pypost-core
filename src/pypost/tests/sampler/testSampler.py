import unittest
from pypost.sampler.Sampler import Sampler
from pypost.tests import DataUtil
from pypost.sampler.SamplerPool import SamplerPool
from pypost.data.DataManager import DataManager


class Test(unittest.TestCase):


    def setUp(self):
        self.sampler = Sampler(DataUtil.createTestManager(), 'testSampler1')
        self.sampler.addSamplerPool(SamplerPool('testPool1', 3))
        self.sampler.addSamplerPool(SamplerPool('testPool2', 1))
        self.sampler.addSamplerPool(SamplerPool('testPool3', 523))
        self.sampler.addSamplerPool(SamplerPool('testPool4', 0))
        self.sampler2 = Sampler(DataManager('testDataManager2'), 'testSampler2')
        self.sampler2.addSamplerPool(SamplerPool('testPool5', 3))


    def test_init(self):
        self.assertEqual(self.sampler.getSamplerName(), 'testSampler1')

    def test_setSamplerIteration(self):
        self.sampler.setSamplerIteration(2)
        self.assertEqual(self.sampler._iterationIndex, 2)

    def test_appendNewSamples(self):
        self.assertTrue(self.sampler.appendNewSamples())

    def test_finalizeSampler(self):
        self.sampler.finalizeSampler(False)
        self.assertDictEqual(self.sampler._samplerMap, {self.sampler2.getSamplerName(): self.sampler2})

    def test_copyPoolsFromSampler(self):
        self.sampler.copyPoolsFromSampler(self.sampler2)
        self.assertIsInstance(self.sampler.getSamplerPool('testPool5'), SamplerPool)

    def test_copySamplerFunctionsFromPool(self): #TODO
        self.sampler.copySamplerFunctionsFromPool(self.sampler2, 'testPool5')
        #self.sampler.getSamplerPool()

    def test_isSamplerFunction(self):
        self.assertTrue(self.sampler.isSamplerFunction('testSampler1'))
        # FIXME: isSamplerFunction() always returns True
        # self.assertFalse(self.sampler.isSamplerFunction('nonExistent'))

    def test_callDataFunction(self): #TODO
        # self.sampler.callDataFunction('testSampler1', newData, parameters)
        pass

    def test_addSamplerPool(self): # TODO
        self.sampler.addSamplerPool(SamplerPool('testPool6', 7))

    def test_getSamplerPool(self):
        self.assertIsInstance(self.sampler.getSamplerPool('testPool3'), SamplerPool)

    def test_getLowLevelSamplers(self):
        self.assertListEqual(self.sampler.getLowLevelSamplers(), [self.sampler2])

    def test_addSamplerFunctionToPool(self): # TODO
        # self.sampler.addSamplerFunctionToPool('testPool1', 'newSamplerFunc1', ???)
        pass

    def test_createSamplesFromPool(self):
        # self.sampler.createSamplesFromPool('testPool1', ???)
        pass

    def test_sampleAllPools(self):
        pass

    def test_createSamplesFromPoolWithPriority(self):
        pass

if __name__ == "__main__":
    unittest.main()