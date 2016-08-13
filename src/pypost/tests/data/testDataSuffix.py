import unittest
import numpy as np
import sys
import os

from numpy.core.numeric import ones
from pypost.data.DataEntry import DataEntry
from pypost.data.DataManager import DataManager
from pypost.data.DataManipulator import DataManipulator
from pypost.common import SettingsManager

from pypost.tests import DataUtil

class TestSuffixManipulator(DataManipulator):

    def __init__(self, dataManager):
        super().__init__(dataManager)


    @DataManipulator.DataDecorator('parameters1', 'parameters2')
    def dummyFunction(self, parameters):
        return parameters + 10

class testDataSuffix(unittest.TestCase):


    def test_dataSuffix(self):

        settings = SettingsManager.getDefaultSettings()
        settings.clean()
        dataManager = DataManager("manager")
        settings.pushSuffixStack('Agent1')

        dataManager.addDataEntry('parameters1', 1)
        dataManager.addDataEntry('parameters2', 1)

        dataManager.addDataAlias('parameters', [('parameters1', ...), ('parameters2', ...)])

        self.assertTrue(dataManager.isDataEntry("parameters1Agent1"))
        self.assertFalse(dataManager.isDataEntry("parameters1"))

        data = dataManager.getDataObject(10)
        data.setDataEntry('parameters1Agent1', ..., np.ones((10,1)) * 5)

        dummyManipulator = TestSuffixManipulator(dataManager)
        dummyManipulator.dummyFunction(data)

        self.assertTrue(np.all(data.getDataEntry("parameters2Agent1") == data.getDataEntry("parameters1Agent1") + 10))
        self.assertTrue(np.all(data.getDataEntry("parametersAgent1") == np.hstack((data.getDataEntry("parameters1Agent1"), data.getDataEntry("parameters2Agent1")))))

        settings.popSuffixStack()



if __name__ == '__main__':
    unittest.main()
