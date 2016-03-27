import unittest
import DataUtil
from sampler.StepSampler import StepSampler


class Test(unittest.TestCase):


    def setUp(self):
        self.sampler = StepSampler(DataUtil.createTestManager(), 'testManager')

    def tearDown(self):
        pass

    def test_init(self):
        self.assertEqual(self.sampler._samplerName, 'testManager')
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
        self.assertIs(self.sampler.isSamplerFunction('sampleInitState'), rs)
        self.assertIs(self.sampler.returnSampler, rs)

    def test_setPolicy(self):
        datamngr = DataUtil.createTestManager()
        rs = Sampler(datamngr, 'policyfunc')
        self.sampler.setInitStateFunction(rs)
        self.assertIs(self.sampler.isSamplerFunction('Policy'), rs)
        self.assertIs(self.sampler.returnSampler, rs)

    def test_setTransitionFunction(self):
        datamngr = DataUtil.createTestManager()
        rs = Sampler(datamngr, 'transitionfunc')
        self.sampler.setInitStateFunction(rs)
        self.assertIs(self.sampler.isSamplerFunction('TransitionSampler'), rs)
        self.assertIs(self.sampler.returnSampler, rs)

    def test_setRewardFunction(self):
        datamngr = DataUtil.createTestManager()
        rs = Sampler(datamngr, 'rewardfunc')
        self.sampler.setInitStateFunction(rs)
        self.assertIs(self.sampler.isSamplerFunction('RewardSampler'), rs)
        self.assertIs(self.sampler.returnSampler, rs)

    def test_endTransition(self):
        pass

    def test_initSamples(self):
        pass

    def test_createSamplesForStep(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()