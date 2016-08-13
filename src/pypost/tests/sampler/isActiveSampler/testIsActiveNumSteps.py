import unittest
from pypost.tests import DataUtil
from pypost.sampler.isActiveSampler.IsActiveNumSteps import IsActiveNumSteps
from pypost.common import SettingsManager


class Test(unittest.TestCase):


    def setUp(self):
        dataManager = DataUtil.createTestManager()
        self.ians = IsActiveNumSteps(dataManager, None, 40)

    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.ians, IsActiveNumSteps)
        # TODO: check linkProperty
        self.assertEqual(self.ians.numTimeSteps, 40)
        datamngr = DataUtil.createTestManager()


    def test_getNumTimeSteps(self):
        # TODO: check linkProperty
        self.assertEqual(self.ians.getNumTimeSteps(), 40)

    def test_setNumTimeSteps(self):
        self.ians.setNumTimeSteps(30)
        self.assertEqual(self.ians.numTimeSteps, 30)

        with self.assertRaises(RuntimeError):
            self.ians.setNumTimeSteps(-1)

    def test_isActiveStep(self):
        self.assertTrue(self.ians.isActiveStep(None, 19))

    def test_toReserve(self):
        # TODO: check linkProperty
        self.assertEqual(self.ians.toReserve(), 40)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
