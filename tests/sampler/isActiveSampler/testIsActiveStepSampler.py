import unittest
from sampler.isActiveSampler.IsActiveStepSampler import IsActiveStepSampler
from data.DataManager import DataManager


class Test(unittest.TestCase):


    def setUp(self):
        self.dataManager = DataManager('testmngr')
        self.ia2s = IsActiveStepSampler(self.dataManager)


    def tearDown(self):
        pass


    def test_init(self):
        self.assertEqual(self.ia2s.stepName, 'timestep')

    def test_isActiveStep(self):
        with self.assertRaises(NotImplementedError):
            self.ia2s.isActiveStep(None, None)

    def test_toReserve(self):
        with self.assertRaises(NotImplementedError):
            self.ia2s.toReserve()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()