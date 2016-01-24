'''
Created on 22.01.2016

@author: Moritz
'''

import numpy as np

from learner.RLLearner import RLLearner
from data.DataManipulator import DataManipulator


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

        self.policyLearner.setWeightName(self.outputWeightName)

        if not self.dataManager.isDataEntry(self.outputWeightName):
            if level is None:
                depth = dataManager.getDataEntryDepth(obj.rewardName)
                self.dataManager.addDataEntryForDepth(
                    depth,
                    obj.outputWeightName,
                    1)
            else:
                level = level + '.' + self.outputWeightName
                self.dataManager.addDataEntry(level, 1)

        self._registerWeightingFunction()

    def updateModel(self, data):
        self.callDataFunction('computeWeighting', data)

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
        p = p / np.sum(p)

        q = np.copy(qWeighting)
        q = q / np.sum(q)

        # FIXME magic number
        index = np.copy(p)
        for x in np.nditer(index):
            index[...] = 1.0 if (p > 10 ^ -10) else 0.0

        # calculate: divKL = sum(p(index)  .* log(p(index) ./ q(index)));
        divKLElements = np.copy(pWeighting)
        for x, y, z in np.nditer(
                [divKL[index], p[index], q[index]], op_flags=['readwrite']):
            for xx, yy in np.nditer([y, z], op_flags=['readwrite']):
                xx[...] = np.log(xx / yy)
            x[...] = x * y
        divKL = np.sum(divKLElements)

        return divKL

    def computeWeighting(self, **args):
        '''
        @return: weights
        '''
        raise NotImplementedError("Not implemented")

    def _registerWeightingFunction(self):
        # FIXME remove magic strings
        # TODO why do we even derive from a Mapping class, if we only access
        # the DataManipulator
        inputs = [self.rewardName]
        inputs.extend(self.additionalInputData)
        self.addDataManipulationFunction(
            "computeWeighting", inputs, [
                self.outputWeightName])
