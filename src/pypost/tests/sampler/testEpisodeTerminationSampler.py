import unittest
from pypost.sampler import TerminationFunction
from pypost.data import DataManager


class Test(unittest.TestCase):


    def setUp(self):
        self.dataManager = DataManager('testmngr')
        self.ia2s = TerminationFunction(self.dataManager, None)


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.ia2s, TerminationFunction)

    def test_isActiveStep(self):
        with self.assertRaises(NotImplementedError):
            self.ia2s.isNonTerminalState(None, None)

    def test_toReserve(self):
        with self.assertRaises(NotImplementedError):
            self.ia2s.toReserve()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
