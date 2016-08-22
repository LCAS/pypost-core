import numpy as np

from pypost.learner.BatchLearner import BatchLearner
from pypost.data.DataManipulator import DataManipulator


class RLByWeightedML(BatchLearner):
    '''
    classdocs
    '''

    def __init__(self, dataManager, policyLearner,
                 rewardName="returns", outputWeight="returnsWeighting", level=None):
        '''
        Constructor
        '''

        BatchLearner.__init__(self, dataManager)

        self.policyLearner = policyLearner

        self.rewardName = rewardName
        self.outputWeightName = outputWeight

        if policyLearner is not None:
            self.policyLearner.setWeightName(self.outputWeightName)

        if not self.dataManager.isDataEntry(self.outputWeightName):
            if level is None:
                depth = dataManager.getDataEntryDepth(self.rewardName)
                subDataManager = dataManager.getSubDataManagerForDepth(depth)
                subDataManager.addDataEntry(self.outputWeightName, 1)
            else:
                level = level + '.' + self.outputWeightName
                self.dataManager.addDataEntry(level, 1)

    def updateModel(self, data):
        data >> self.computeWeighting

        if self.policyLearner is not None:
            data >> self.policyLearner


    def getKLDivergence(self, qWeighting, pWeighting):
        p = np.copy(pWeighting)
        np.divide(p, np.sum(p), p)

        q = np.copy(qWeighting)
        np.divide(q, np.sum(q), q)

        # FIXME magic number
        index = np.zeros(len(p), bool)
        for i in range(0, len(p)):
            index[i] = True if (p[i] > 10e-10) else False

        divKL = np.sum(p[index] * np.log(np.divide(p[index], q[index])))
        #print(divKL)
        return divKL

    @DataManipulator.DataMethod(['self.rewardName'], ['self.outputWeightName'])
    def computeWeighting(self, **args):
        '''
        :returns: weights
        '''
        raise NotImplementedError("Not implemented")

