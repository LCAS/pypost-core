import unittest
from pypost.sampler.isActiveSampler.IsActiveStepSampler import IsActiveStepSampler
from pypost.data.DataManager import DataManager


class Test(unittest.TestCase):


    def setUp(self):
        self.dataManager = DataManager('testmngr')
        self.ia2s = IsActiveStepSampler(self.dataManager, None)


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.ia2s, IsActiveStepSampler)

    def test_isActiveStep(self):
        with self.assertRaises(NotImplementedError):
            self.ia2s.isActiveStep(None, None)

    def test_toReserve(self):
        with self.assertRaises(NotImplementedError):
            self.ia2s.toReserve()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
