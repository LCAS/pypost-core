import unittest
import DataUtil
from sampler.EpisodeSampler import EpisodeSampler
from data.DataManager import DataManager
from sampler.Sampler import Sampler


class Test(unittest.TestCase):


    def setUp(self):
        self.sampler = EpisodeSampler()


    def tearDown(self):
        pass


    def test_init(self):
        self.assertIsInstance(self.sampler, EpisodeSampler)
        self.assertEqual(self.sampler._samplerName, 'episodes')
        self.assertEqual(self.sampler.dataManager.name, 'episodes')
        self.assertIsNotNone(self.sampler.getSamplerPool('InitEpisode'))
        self.assertIsNotNone(self.sampler.getSamplerPool('ParameterPolicy'))
        self.assertIsNotNone(self.sampler.getSamplerPool('Episodes'))
        self.assertIsNotNone(self.sampler.getSamplerPool('FinalReward'))
        self.assertIsNotNone(self.sampler.getSamplerPool('Return'))
        sampler2  = EpisodeSampler(DataManager('testManager'), 'testSampler2')
        self.assertIsInstance(sampler2, EpisodeSampler)
        self.assertEqual(sampler2._samplerName, 'testSampler2')
        self.assertEqual(sampler2.dataManager.name, 'testManager')
        

    def test_getEpisodeDataManager(self):
        self.assertIsInstance(self.sampler.getEpisodeDataManager(), DataManager)

    def test_setFinalRewardSampler(self):
        datamngr = DataUtil.createTestManager()
        rs = Sampler(datamngr, 'reward')
        self.sampler.setFinalRewardSampler(rs, 'testSampler', True)
        self.assertTrue(self.sampler.isSamplerFunction('FinalReward'))
        self.assertIs(self.sampler.returnSampler, rs)

        datamngr = DataUtil.createTestManager2()
        rs2 = Sampler(datamngr, 'reward')
        self.sampler.setFinalRewardSampler(rs2, isReturnSampler=False)
        self.assertTrue(self.sampler.isSamplerFunction('FinalReward'))
        self.assertIs(self.sampler.returnSampler, rs)

        rs3 = Sampler(DataManager('Testmngr3'), 'reward3')
        self.sampler.setFinalRewardSampler(rs3, 'testSampler')
        self.assertTrue(self.sampler.isSamplerFunction('FinalReward'))
        self.assertIs(self.sampler.returnSampler, rs3)

    def test_setReturnFunction(self):
        rs = Sampler(DataManager('TestmngrH'), 'rewardH')
        self.sampler.setReturnFunction(rs)
        self.assertTrue(self.sampler.isSamplerFunction('Return'))
        self.assertIs(self.sampler.returnSampler, rs)

        datamngr = DataUtil.createTestManager2()
        rs2 = Sampler(datamngr, 'return')
        self.sampler.setReturnFunction(rs2, 'noRet')
        self.assertTrue(self.sampler.isSamplerFunction('Return'))
        self.assertIsNot(self.sampler.returnSampler, rs2)

    def test_setParameterPolicy(self):
        datamngr = DataUtil.createTestManager()
        rs = Sampler(datamngr, 'policy')
        self.sampler.setParameterPolicy(rs)
        self.assertTrue(self.sampler.isSamplerFunction('ParameterPolicy'))
        self.assertIs(self.sampler.parameterPolicy, rs)

        datamngr = DataUtil.createTestManager()
        rs2 = Sampler(datamngr, 'policy')
        self.sampler.setParameterPolicy(rs2, 'sp')
        self.assertTrue(self.sampler.isSamplerFunction('ParameterPolicy'))
        self.assertIs(self.sampler.parameterPolicy, rs2)

        datamngr = DataUtil.createTestManager()
        rs3 = Sampler(datamngr, 'policy')
        self.sampler.setParameterPolicy(rs3, 'samParam', False)
        self.assertTrue(self.sampler.isSamplerFunction('ParameterPolicy'))
        self.assertIsNot(self.sampler.parameterPolicy, rs3)

    def test_setContextSampler(self):
        datamngr = DataUtil.createTestManager()
        rs = Sampler(datamngr, 'reward')
        self.sampler.setContextSampler(rs)
        self.assertTrue(self.sampler.isSamplerFunction('InitEpisode'))
        self.assertIs(self.sampler.contextDistribution, rs)

        datamngr = DataUtil.createTestManager()
        rs2 = Sampler(datamngr, 'reward')
        self.sampler.setContextSampler(rs2, 'cs')
        self.assertTrue(self.sampler.isSamplerFunction('InitEpisode'))
        self.assertIs(self.sampler.contextDistribution, rs2)

        datamngr = DataUtil.createTestManager()
        rs3 = Sampler(datamngr, 'reward')
        self.sampler.setContextSampler(rs3, 'conSam', False)
        self.assertTrue(self.sampler.isSamplerFunction('InitEpisode'))
        self.assertIsNot(self.sampler.contextDistribution, rs3)

    def test_flushReturnFunction(self):
        self.test_setReturnFunction()
        self.sampler.flushReturnFunction()
        self.assertListEqual(self.sampler.getSamplerPool("Return").samplerList, [])

    def test_flushFinalRewardFunction(self):
        self.test_setFinalRewardSampler()
        self.sampler.flushFinalRewardFunction()
        self.assertListEqual(self.sampler.getSamplerPool("FinalReward").samplerList, [])

    def test_flushParameterPolicy(self):
        self.test_setParameterPolicy()
        self.sampler.flushParameterPolicy()
        self.assertListEqual(self.sampler.getSamplerPool("ParameterPolicy").samplerList, [])

    def test_flushContextSampler(self):
        self.test_setParameterPolicy()
        self.sampler.flushContextSampler()
        self.assertListEqual(self.sampler.getSamplerPool("InitEpisode").samplerList, [])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()