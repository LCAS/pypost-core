import unittest
import DataUtil
from sampler.isActiveSampler.IsActiveNumSteps import IsActiveNumSteps
from common import SettingsManager


class Test(unittest.TestCase):


    def setUp(self):
        dataManager = DataUtil.createTestManager()
        self.ians = IsActiveNumSteps(dataManager, None, 20)


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.ians, IsActiveNumSteps)
        self.assertEqual(self.ians._numTimeSteps, 20)
        datamngr = DataUtil.createTestManager()
        testIans = IsActiveNumSteps(datamngr, 'testName', 20)
        self.assertIsNotNone(testIans._manipulationFunctions)
        

    def test_getNumTimeSteps(self):
        self.assertEqual(self.ians.getNumTimeSteps(), 20)

    def test_setNumTimeSteps(self):
        self.ians.setNumTimeSteps(30)
        self.assertEqual(self.ians._numTimeSteps, 30)

        with self.assertRaises(RuntimeError):
            self.ians.setNumTimeSteps(-1)

    def test_isActiveStep(self):
        self.assertTrue(self.ians.isActiveStep(None, 19))

    def test_toReserve(self):
        self.assertEqual(self.ians.toReserve(), 20)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()