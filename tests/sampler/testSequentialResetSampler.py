import unittest
import DataUtil
from sampler.SequentialResetSampler import SequentialResetSampler
from data.Data import Data
from data.DataStructure import DataStructure


class Test(unittest.TestCase):


    def setUp(self):
        self.dataManager = DataUtil.createTestManager()
        self.sampler = SequentialResetSampler(dataManager, 'testSampler')

    def tearDown(self):
        pass

    def test_init(self):
        pass

    def test_createSamples(self):
        datamngr = DataUtil.createTestManager()
        data = Data(datamngr, DataStructure(4))
        self.sampler.createSamples(data)

    def test_getNumSamples(self):
        pass

    def test_endTransition(self):
        pass

    def test_initSamples(self):
        pass

    def test_createSamplesForStep(self):
        pass

    def test_adjustReservedStorage(self):
        pass

    def _selectActiveIdxs(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()