#  #!/usr/bin/python

from pypost.experiments.Experiment import Experiment
from pypost.plotter.PlotterEvaluations import PlotterErrorBars
from pypost.plotter.PlotterEvaluations import PlotterTrials
from pypost.tutorials.experiments.DummyTrial import DummyTrial


def runExperiment(numTrials):
    # Create directories if non-existent


    experiment = Experiment('/tmp', 'testCategory', DummyTrial)

    experiment.defaultSettings.temperature = 2
    experiment.create()

    evaluation1 = experiment.addEvaluationCollection(['temperature'], [0.1, 1, 2, 3], numTrials = 3)

    experiment.startLocal()

    data = experiment.getEvaluationData(evaluation1)

    plotter = PlotterTrials(data.dataManager, 'avgReturns', 'temperature', logSpaceY=True, useEpisodesXLabel=True, legendPerTrial = True)
    data[Ellipsis] >> plotter

    print('Hello')


if __name__ == '__main__':

    runExperiment(2)

