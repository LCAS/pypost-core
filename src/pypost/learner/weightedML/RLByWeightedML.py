import numpy as np

from pypost.learner.RLLearner import RLLearner
from pypost.data.DataManipulator import DataManipulator
from pypost.data.DataPreprocessor import DataPreprocessor


class RLByWeightedML(RLLearner, DataManipulator, object):
    '''
    classdocs
    '''

    def __init__(self, dataManager, policyLearner,
                 rewardName=None, outputWeight=None, level=None):
        '''
        Constructor
        '''

        RLLearner.__init__(self)
        DataManipulator.__init__(self, dataManager)

        self.dataManager = dataManager
        self.outputWeightName = ''
        self.rewardName = ''

        # FIXME ... already included in mapping?
        self.additionalInputData = []

        self.policyLearner = policyLearner

        if rewardName is not None:
            self.rewardName = rewardName
        else:
            # FIXME replace magic constant returns by settings
            self.rewardName = "returns"

        if outputWeight is not None:
            self.outputWeightName = outputWeight
        else:
            # FIXME replace magic constant returns by settings
            self.outputWeightName = self.rewardName + 'Weighting'

        if policyLearner is not None:
            self.policyLearner.outputWeightName = self.outputWeightName

        if not self.dataManager.isDataEntry(self.outputWeightName):
            if level is None:
                depth = dataManager.getDataEntryDepth(self.rewardName)
                subDataManager = dataManager.getSubDataManagerForDepth(depth)
                subDataManager.addDataEntry(self.outputWeightName, 1)
            else:
                level = level + '.' + self.outputWeightName
                self.dataManager.addDataEntry(level, 1)

        self._registerWeightingFunction()

    def updateModel(self, data):
        self.callDataFunction('computeWeighting', data, ...) # TODO check this

        if self.policyLearner is not None:
            self.policyLearner.updateModel(data)

    def setWeightName(self, outputWeightName):
        self.outputWeightName = outputWeightName
        self._registerWeightingFunction()

    def setRewardName(self, rewardName):
        self.rewardName = rewardName
        self._registerWeightingFunction()

    def setAdditionalInputs(self, inputs, append=False):
        if append:
            self.additionalInputData.extend(inputs)
        else:
            self.additionalInputData = list(inputs)

        self._registerWeightingFunction()

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

    def computeWeighting(self, **args):
        '''
        :returns: weights
        '''
        raise NotImplementedError("Not implemented")

    def _registerWeightingFunction(self):
        inputs = [self.rewardName]
        inputs.extend(self.additionalInputData)
        self.addDataManipulationFunction(self.computeWeighting, inputs,
                                         [self.outputWeightName])
