import unittest
from pypost.policy.Policy import Policy


class testPolicy(unittest.TestCase):

    def setUp(self):
        def pfunc(a, b, c):
            return (a + b) * c
        self.policy = Policy(pfunc, 'default')

    def tearDown(self):
        pass

    def test_init(self):
        self.assertEqual(self.policy._poolName, 'default')
        self.assertEqual(self.policy._policyName, 'sampleDefault')
        policy2 = Policy(self.policy._policyFunction, 'poolA', 'AAA')
        self.assertEqual(policy2._policyName, 'AAA')

    def test_getPolicyFunction(self):
        self.assertIsNotNone(self.policy.getPolicyFunction())

    def test_getPolicyName(self):
        self.assertEqual(self.policy.getPolicyName(), 'sampleDefault')

    def test_getPoolName(self):
        self.assertEqual(self.policy.getPoolName(), 'default')

    def test_call(self):
        self.assertEqual(self.policy(2, 3, 7), 35)
        self.assertEqual(self.policy(5, 11, c=27), 432)
        self.assertEqual(self.policy(1, c=3, b=2), 9)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
