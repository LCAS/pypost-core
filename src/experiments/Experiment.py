'''
Created on 26.01.2016

@author: Sebastian Kreutzer
'''
import os
import getpass


class Experiment(object):
    '''
    TODO: Document this shit
    '''

    root = 'Experiments/data'

    def __init__(self, category, taskName):
        '''
        Constructor
        '''
        self.category = category
        self.taskName = taskName
        self.path = os.path.join(Experiment.root, category, taskName)

        self.trialToEvaluationMap = {}
        self.trialIndexToDirectorymap = {}
        self.user = getpass.getuser()

    @staticmethod
    def addToDataBase(newExperiment):
        raise RuntimeError("Not implemented")

    def addEvaluationCollection(self, parameterNames,
                                parameterValues, numTrials):
        raise RuntimeError("Not implemented")

    def startLocal(self, trialIndices):
        raise RuntimeError("Not implemented")
