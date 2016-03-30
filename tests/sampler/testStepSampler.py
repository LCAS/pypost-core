import unittest
import DataUtil
from sampler.StepSampler import StepSampler
from sampler.Sampler import Sampler


class testStepSampler(unittest.TestCase):


    def setUp(self):
        self.sampler = StepSampler(DataUtil.createTestManager(), 'episodes')

    def tearDown(self):
        pass

    def test_init(self):
        self.assertIsInstance(self.sampler, StepSampler)
        self.assertEqual(self.sampler._samplerName, 'episodes')
        self.assertEqual(self.sampler.dataManager.name, 'episodes')
        self.assertIsNotNone(self.sampler.getSamplerPool('InitSamples'))
        self.assertIsNotNone(self.sampler.getSamplerPool('Policy'))
        self.assertIsNotNone(self.sampler.getSamplerPool('TransitionSampler'))
        self.assertIsNotNone(self.sampler.getSamplerPool('RewardSampler'))
        self.assertTrue(self.sampler._dataManager.isDataEntry('timeSteps'))

    def test_setInitStateFunction(self):
        datamngr = DataUtil.createTestManager()
        rs = Sampler(datamngr, 'initstatefunc')
        self.sampler.setInitStateFunction(rs)
        self.assertTrue(self.sampler.isSamplerFunction('sampleInitState'))

    def test_setPolicy(self):
        datamngr = DataUtil.createTestManager()
        rs = Sampler(datamngr, 'policyfunc')
        self.sampler.setInitStateFunction(rs)
        self.assertTrue(self.sampler.isSamplerFunction('Policy'))

    def test_setTransitionFunction(self):
        datamngr = DataUtil.createTestManager()
        rs = Sampler(datamngr, 'transitionfunc')
        self.sampler.setInitStateFunction(rs)
        self.assertTrue(self.sampler.isSamplerFunction('TransitionSampler'))

    def test_setRewardFunction(self):
        datamngr = DataUtil.createTestManager()
        rs = Sampler(datamngr, 'rewardfunc')
        self.sampler.setInitStateFunction(rs)
        self.assertTrue(self.sampler.isSamplerFunction('RewardSampler'))

    def test_endTransition(self):
        pass

    def test_initSamples(self):
        pass

    def test_createSamplesForStep(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()