from pypost.data.Data import Data
from pypost.data.DataManipulator import DataManipulator
from pypost.data.DataManipulator import CallType
from pypost.mappings.Mapping import Mapping

import numpy as np
import matplotlib
# matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
# plt.ion()
from cycler import cycler
from matplotlib.pyplot import cm
from itertools import cycle
from matplotlib2tikz import save as tikz_save


class PlotterEvaluationsBase(Mapping):

    def __init__(self, dataManager, plottingVariable, legendParameter, logSpaceY = False, useEpisodesXLabel = False, smooth_data=False):
        '''
        Constructor

        :change: dataManager was removed from function arguments and is now a constructor argument.
        '''
        Mapping.__init__(self, dataManager, [], [], 'plotter' + plottingVariable)

        self.plottingVariable = plottingVariable
        self.legendParameter = legendParameter
        self.legendHandles= []
        self.colorCycle = cycle(np.linspace(0,1,10))
        self.colorMap = matplotlib.cm.tab10  # cm.get_cmap('rainbow')
        self.smooth_data = smooth_data

        if (not useEpisodesXLabel):
            self.xAxisLabel = 'iterations'
        else:
            self.xAxisLabel = 'episodes'

        self.yAxisLabel = plottingVariable

        self.logSpaceY = logSpaceY
        self.useEpisodesXLabel = useEpisodesXLabel

    @Mapping.MappingMethod(takesData=True)
    def plotFunction(self, data):
        plt.figure()
        self.colorCycle = cycle(np.linspace(0, 1, 10))

        self.legendHandles = []
        data >> self.plotFunctionSingle
        plt.legend(handles=self.legendHandles)

        plt.xlabel(self.xAxisLabel)
        plt.ylabel(self.yAxisLabel)

        plt.autoscale(enable=True, axis='x', tight=True)
        plt.pause(0.01)
        plt.show()

    # TODO: how to give arguments like filename, image specs?
    @DataManipulator.DataMethod(takesData=True, inputArguments=[], outputArguments=[])
    def plotSaveFunction(self, data, filename):
        plt.figure()
        self.colorCycle = cycle(np.linspace(0, 1, 10))

        self.legendHandles = []
        data >> self.plotFunctionSingle
        plt.legend(handles=self.legendHandles)

        plt.xlabel(self.xAxisLabel)
        plt.ylabel(self.yAxisLabel)

        plt.autoscale(enable=True, axis='x', tight=True)
        plt.gca().set_ylim((-100, 8000))
        plt.savefig('/tmp/' + filename + '.pdf')
        tikz_save(
            '/tmp/' + filename + '.tex',
            figureheight='\\figureheight',
            figurewidth='\\figurewidth'
        )

    @DataManipulator.DataMethod(inputArguments=['self.plottingVariable' + '__T', 'numEpisodes', 'self.legendParameter'], outputArguments=[], callType=CallType.PER_EPISODE)
    def plotFunctionSingle(self, plotData, numEpisodes, legendParameterVal = []):
        raise ValueError('This is an abstract base class')


class PlotterErrorBars(PlotterEvaluationsBase):

    def __init__(self, dataManager, plottingVariable, legendParameter, logSpaceY = False, useEpisodesXLabel = False, useMedian = False,
                 smooth_data=False,):
        '''
        Constructor

        :change: dataManager was removed from function arguments and is now a constructor argument.
        '''
        PlotterEvaluationsBase.__init__(self, dataManager, plottingVariable, legendParameter,
                                        logSpaceY = logSpaceY,
                                        useEpisodesXLabel = useEpisodesXLabel,
                                        smooth_data=smooth_data)

        self.useMedian = useMedian

    @DataManipulator.DataMethod(inputArguments=['self.plottingVariable' + '__T', 'numEpisodes', 'self.legendParameter'], outputArguments=[], callType=CallType.PER_EPISODE)
    def plotFunctionSingle(self, plotData, numEpisodes, legendParameterVal = []):

        (curve, lowerBound, upperBound) = self.getPlotWithErrorBars(plotData)
        if (self.logSpaceY):
            # this assumes that the reward can only be negative

            curve = np.log10(-curve)
            lowerBound = np.log10(-lowerBound)
            upperBound[upperBound > - 0.01] = - 0.01
            upperBound = np.log10(-upperBound)

            tmp = lowerBound
            lowerBound = upperBound
            upperBound = tmp

        if (self.useEpisodesXLabel):
            x = np.array(range(0, curve.shape[0]))
            x = x * numEpisodes[0]
        if self.smooth_data>0:
            def smooth(y, box_pts):
                box = np.ones(box_pts) / box_pts
                y_smooth = np.convolve(y, box, mode='same')
                return y_smooth

            # TODO: 20 is just an arbitrary number
            curve = curve[0::20]
            lowerBound = lowerBound[0::20]
            upperBound = upperBound[0::20]

            curve = np.hstack([np.repeat(curve[0], self.smooth_data, axis=0),
                               curve,
                               np.repeat(curve[-1], self.smooth_data, axis=0)])
            curve = smooth(curve, self.smooth_data)
            curve = curve[self.smooth_data:-self.smooth_data]
            lowerBound = np.hstack([np.repeat(lowerBound[0], self.smooth_data, axis=0),
                                    lowerBound,
                                    np.repeat(lowerBound[-1], self.smooth_data, axis=0)])
            lowerBound = smooth(lowerBound, self.smooth_data)
            lowerBound = lowerBound[self.smooth_data:-self.smooth_data]
            upperBound = np.hstack([np.repeat(upperBound[0], self.smooth_data, axis=0),
                                    upperBound,
                                    np.repeat(upperBound[-1], self.smooth_data, axis=0)])
            upperBound = smooth(upperBound, self.smooth_data)
            upperBound = upperBound[self.smooth_data:-self.smooth_data]

            x = range(0, curve.shape[0])
        else:
            x = range(0, curve.shape[0])

        legendString = 'Line{}'.format(len(self.legendHandles))
        color = self.colorMap(next(self.colorCycle))

        if legendParameterVal:
            legendString = self.legendParameter + '={0}'.format(legendParameterVal[0,0])

        plt.fill_between(x, lowerBound, upperBound, color = color, alpha = 0.5)

        newHandle = plt.plot(x, curve, color = color, label = legendString)
        self.legendHandles.append(newHandle[0])


    def getPlotWithErrorBars(self, plotData):

        if (self.useMedian):
            medianPlot = np.median(plotData, axis = 1)
            lowerBound = np.percentile(plotData, 10, axis = 1)
            upperBound = np.percentile(plotData, 90, axis=1)
            return (medianPlot, lowerBound, upperBound)
        else:
            meanPlot = np.mean(plotData, axis=1)
            stdPlot = np.std(plotData, axis=1)
            return (meanPlot, meanPlot - stdPlot, meanPlot + stdPlot)

class PlotterTrials(PlotterEvaluationsBase):

    def __init__(self, dataManager, plottingVariable, legendParameter, logSpaceY = False, useEpisodesXLabel = False, legendPerTrial = False,
                 smooth_data=False,):
        '''
        Constructor

        :change: dataManager was removed from function arguments and is now a constructor argument.
        '''
        PlotterEvaluationsBase.__init__(self, dataManager, plottingVariable, legendParameter, logSpaceY = logSpaceY, useEpisodesXLabel = useEpisodesXLabel,
                                        smooth_data=smooth_data)
        self.legendPerTrial = legendPerTrial

    @DataManipulator.DataMethod(inputArguments=['self.plottingVariable' + '__T', 'numEpisodes', 'self.legendParameter'], outputArguments=[], callType=CallType.PER_EPISODE)
    def plotFunctionSingle(self, plotData, numEpisodes, legendParameterVal = []):

        if (self.logSpaceY):
            # this assumes that the reward can only be negative

            curve = np.log10(-plotData)
        else:
            curve = plotData

        if self.smooth_data>0:
            def smooth(y, box_pts):
                box = np.ones(box_pts) / box_pts
                y_smooth = []
                for i in range(y.shape[1]):
                    y_smooth.append(np.convolve(y[:,i], box, mode='same'))
                return np.vstack(y_smooth).T

            # TODO: 20 is just an arbitrary number
            curve = curve[0::20, :]
            curve = np.vstack([np.repeat(curve[0:1, :], self.smooth_data, axis=0),
                               curve,
                               np.repeat(curve[-1:,:], self.smooth_data, axis=0)])
            curve = smooth(curve, self.smooth_data)
            curve = curve[self.smooth_data:-self.smooth_data]

            x = range(0, curve.shape[0])

        if (self.useEpisodesXLabel):
            x = range(0, curve.shape[0])
            x = x * numEpisodes[0]
        else:
            x = range(0, curve.shape[0])

        if (not self.legendPerTrial):
            legendString = 'Line{}'.format(len(self.legendHandles))
            color = self.colorMap(next(self.colorCycle))

            if legendParameterVal:
                legendString = self.legendParameter + '={0}'.format(legendParameterVal[0, 0])

            newHandle = plt.plot(x, curve[:,0], color = color, label = legendString)
            self.legendHandles.append(newHandle[0])

            for i in range(1,curve.shape[1]):
                plt.plot(x, curve[:, i], color = color, label=legendString)

        else:

            for i in range(0, curve.shape[1]):
                legendString = 'Line{}'.format(len(self.legendHandles))

                color = self.colorMap(next(self.colorCycle))

                if legendParameterVal:
                    legendString = self.legendParameter + '={0}'.format(legendParameterVal[0, 0])

                newHandle = plt.plot(x, curve[:, 0], color=color, label=legendString)
                self.legendHandles.append(newHandle[0])

                plt.plot(x, curve[:, i], color=color, label=legendString)

