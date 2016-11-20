from pypost.data.DataManipulator import DataManipulator
from pypost.mappings import Mapping
from pypost.data import CallType

import abc


# Todo Periodicity? Not supported by Data Manager in Python
class ReturnSummedReward(Mapping):

    def __init__(self, dataManager):

        dataManager.addDataEntry('returns', 1)
        super().__init__(dataManager, ['rewards'], ['returns'])


    @Mapping.MappingMethod(callType=CallType.PER_EPISODE)
    def computeReturn(self, rewards):
        return sum(rewards)

