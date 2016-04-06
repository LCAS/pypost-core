from sampler.IndependentSampler import IndependentSampler
from sampler.SamplerPool import SamplerPool
from functools import reduce
import numpy as np


class GridSampler(IndependentSampler):
    '''
    Sets up an

    Methods (annotated):
    def __init__(self, dataManager: data.DataManager, samplerName: str, outputVariable: list, nSamples: int) -> None
    def getNumSamples(self, data=None, *args) -> int
    def sampleGrid(self, numElements: int) -> list of Boolean
    '''

    def __init__(self, dataManager, samplerName, outputVariables, nSamples):
        '''
        :param dataManager: DataManager this sampler operates on
        :param samplerName: name of this sampler
        :param outputVariables: list containing aliases to output
        :param nSamples: number of samples for each grid cell

        :change: outputVariables has to be an array of arrays
        #FIXME grid
        '''
        super().__init__(dataManager, samplerName)

        self._minValues = None
        '''
        Minimal values of samples. nx1 vector
        '''

        self._maxValues = None
        '''
        Maximal values of samples. nx1 vector
        '''

        self._nSamples = nSamples
        '''
        Number of samples for each individual grid cell. nx1 vector
        '''

        # TODO use array=[func(i) for i in iterator] scheme
        namesCell = [None] * len(outputVariables)
        self._minValues = [None] * len(outputVariables)
        self._maxValues = [None] * len(outputVariables)
        for index, cell in enumerate(outputVariables):
            names = self._dataManager.getDataManagerForEntry(
                cell).dataAliases[cell].entryNames.copy()
            namesCell[index] = names

            self._minValues[index] = [None] * len(names)
            self._maxValues[index] = [None] * len(names)
            for nameIndex, name in enumerate(names):
                dataEntries = self._dataManager.getDataManagerForEntry(
                    name).dataEntries(name)
                self._minValues[index][nameIndex] = dataEntries.minRange.copy()
                self._maxValues[index][nameIndex] = dataEntries.maxRange.copy()
        # FIXME check correct code port of loop above

        # make sampler pool
        self.addSamplerPool(SamplerPool('gridSamplerPool', 1))

        # register function
        self.addDataManipulationFunction(self.sampleGrid, {}, outputVariables)
        self.addSamplerFunctionToPool('gridSamplerPool', 'sampleGrid', self, 0)

    def getNumSamples(self, data=None, *args):
        # @mw ASK: parameters?
        return np.prod(self._nSamples)

    def sampleGrid(self, numElements):
        # ASK why do we even have a numElements parameter, if its value is
        #elements = self.getNumSamples()
        # already predetermined. was already comented out
        # if elements != numElements:
        #    raise RuntimeError("GridSampler: wrong number of samples")

        numdims = np.prod(self._minValues)

        # create array with possible values for each dim
        possibleValues = [
            np.linspace(
                self._minValues[x],
                self._maxValues[x],
                self._nSamples[x],
                True) for x in range(
                numdims)]

        # generate output grid
        grids = [np.mgrid[possibleValues] for i in range(numdims)]

        output = [True for i in range(numdims)]

        return output
