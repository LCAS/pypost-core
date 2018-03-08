from itertools import cycle

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import cm

from pypost.mappings.Mapping import Mapping


class PlotterTrajectories(Mapping):

    def __init__(self, dataManager, plottingVariable, indices):
        '''
        Constructor

        :change: dataManager was removed from function arguments and is now a constructor argument.
        '''
        Mapping.__init__(self, dataManager, [], [], 'plotter' + plottingVariable)

        self.plottingVariable = plottingVariable

        self.colorCycle = cycle(np.linspace(0,1,10))
        self.colorMap = cm.get_cmap('rainbow')

        self.xAxisLabel = 'timeSteps'

        self.yAxisLabel = plottingVariable

        self.indices = indices

    @Mapping.MappingMethod(takesData=True)
    def plotFunction(self, data):
        self.colorCycle = cycle(np.linspace(0, 1, 10))

        self.legendHandles = []

        plotData = data.getDataEntry(self.plottingVariable + '__T')

        for i in range(0, len(self.indices)):

            plt.figure()

            index = self.indices[i]
            numDim = plotData.shape[1]

            step = self.dataManager.getNumDimensions(self.plottingVariable)
            plotData_i = plotData[:, slice(index, numDim, step)]
            legendHandles = []
            for j in range(0, plotData_i.shape[1]):
                label = 'Episode %d' % j
                handle = plt.plot(plotData_i[:, j], label = label)
                legendHandles.append(handle[0])

            plt.legend(handles=legendHandles)

            plt.xlabel(self.xAxisLabel)
            plt.ylabel('%s%d' % (self.yAxisLabel, index))

            plt.autoscale(enable=True, axis='x', tight=True)

        #plt.show()


class PlotterTrajectoryDistribution(Mapping):

    def __init__(self, dataManager, plottingVariable, indices):
        '''
        Constructor

        :change: dataManager was removed from function arguments and is now a constructor argument.
        '''
        Mapping.__init__(self, dataManager, [], [], 'plotter' + plottingVariable)

        self.plottingVariable = plottingVariable

        self.colorCycle = cycle(np.linspace(0,1,10))
        self.colorMap = cm.get_cmap('rainbow')

        self.xAxisLabel = 'timeSteps'

        self.yAxisLabel = plottingVariable

        self.indices = indices

    @Mapping.MappingMethod(takesData=True)
    def plotFunction(self, data):
        self.colorCycle = cycle(np.linspace(0, 1, 10))

        legendHandles = []

        plotData = data.getDataEntry(self.plottingVariable + '__T')

        plt.figure()

        for i in range(0, len(self.indices)):

            index = self.indices[i]
            numDim = plotData.shape[1]

            step = self.dataManager.getNumDimensions(self.plottingVariable)
            plotData_i = plotData[:, slice(index, numDim, step)]

            curve = np.mean(plotData_i, axis=1)
            curve_std = np.std(plotData_i, axis=1)

            lowerBound = curve - 2 * curve_std
            upperBound = curve + 2 * curve_std

            x = range(0,plotData_i.shape[0])
            color = self.colorMap(next(self.colorCycle))

            plt.fill_between(x, lowerBound, upperBound, color=color, alpha=0.5)

            label = '%s%d' % (self.plottingVariable, index)
            newHandle = plt.plot(x, curve, color=color, label=label)
            legendHandles.append(newHandle[0])


        plt.legend(handles=legendHandles)

        plt.xlabel(self.xAxisLabel)
        plt.ylabel(self.yAxisLabel)

        plt.autoscale(enable=True, axis='x', tight=True)

        #plt.show()

