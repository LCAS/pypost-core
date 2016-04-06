import unittest
import DataUtil
from sampler.GridSampler import GridSampler


class Test(unittest.TestCase):


    def setUp(self):
        self.dataManager = DataUtil.createTestManager()
        self.sampler = GridSampler(self.dataManager, 'testSampler1', ['parameters'], 3)

    def tearDown(self):
        pass


    def test_init(self):
        self.assertEqual()

    def test_getNumSamples(self):
        pass

    def test_sampleGrid(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
