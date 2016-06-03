import unittest
import sys
import numpy as np
import pprint as pp

from pypost.sampler.EpisodeSampler import EpisodeSampler
from pypost.data.DataEntry import DataEntry
from pypost.data.DataManager import DataManager
from tutorials.sampler.TestEnvironment import TestEnvironment

'''
In this tutorial, we will learn how to create samples and merge them
using the `mergeData`-function.
'''

sampler = EpisodeSampler()
environment = TestEnvironment(sampler.getEpisodeDataManager())

sampler.setContextSampler(environment)
sampler.setParameterPolicy(environment)
sampler.setReturnFunction(environment)

dataManager = sampler.getEpisodeDataManager()
newData = dataManager.getDataObject(10)
newData2 = dataManager.getDataObject(0)

sampler.numSamples = 10
sampler.setParallelSampling(True)
print('Generating Data\n')
sampler.createSamples(newData)
pp.pprint(newData.dataStructure.dataStructureLocalLayer)

#print('Merging Data\n')
#newData2.mergeData(newData)
#pp.pprint(newData.dataStructure.dataStructureLocalLayer)

#print('Generating Data 2nd time\n')
#sampler.createSamples(newData)

#print('Merging Data\n')
#newData2.mergeData(newData)
#pp.pprint(newData2.dataStructure.dataStructureLocalLayer)
