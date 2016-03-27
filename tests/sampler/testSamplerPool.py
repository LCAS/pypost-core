'''
Created on 14 Feb 2016

@author: daniele
'''
import unittest
from sampler.SamplerPool import SamplerPool
from sampler.Sampler import Sampler
from data.DataManager import DataManager


class Test(unittest.TestCase):


    def setUp(self):
        self.samplerPool = SamplerPool('testPool1', 5)


    def test_init(self):
        self.assertIsInstance(self.samplerPool.samplerList, list)
        self.assertEqual(self.samplerPool.getName(), 'testPool1')
        self.assertEqual(self.samplerPool.getPriority(), 5)

    def test_getName(self):
        self.samplerPool._setName('newName')
        self.assertEqual(self.samplerPool.getName(), 'newName')

    def test_getPriority(self):
        self.samplerPool._setPriority(10)
        self.assertEqual(self.samplerPool.getPriority(), 10)
        with self.assertRaises(RuntimeError):
            self.samplerPool._setPriority(-1)

    def test_flush(self):
        self.samplerPool.samplerList = [Sampler(DataManager('testManager1'), 'testSampler1'), Sampler(DataManager('testManager2'), 'testSampler2')]
        self.samplerPool.flush()
        self.assertListEqual(self.samplerPool.samplerList, [])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()