from sampler import EpisodeSampler
from common import Settings
from learner.episodicRL import EpisodicPower

trial, settingsEval = Experiments.getTrialForScript()

if trial.isConfigure:
    settings = Common.Settings()
    settings.setProperty("numParameters", 15)
    settings.setProperty("numContexts", 0)
    settings.setProperty("numSamplesEpisodes", 10)
    settings.setProperty("numParameters", 15)
    settings.setProperty("numIterations", 2000)
    trial.configure(settings)

    sampler = EpisodeSampler()
    dataManager = sampler.getDataManager()

    returnSampler = RosenbrockReward(
        sampler,
        settings.numContexts,
        settings.numParameters)

    parameterPolicy = GaussianParameterPolicy(dataManager)
    policyLearner = EpisodicPower(
        dataManager,
        None)
    # FIXME None should be a policyLearner instance ... is this parameter even used?
    # from the outcommented CreateFromTrial function in EpisodicPower we
    # would set trial.parameterPolicyLearner and trial.dataManager

    sampler.setParameterPolicy(parameterPolicy)
    sampler.setReturnFunction(returnSampler)

    dataManager.finalizeDataManager()

# FIXME variables used below are not defined if trial.isConfigure is not
# executed
if trial.isStart:
    newData = dataManager.getDataObject.getDataObject(10)

    parameterPolicy.initObject()

    for i in range(0, settings.numIterations - 1):
        sampler.createSamples(newData)

        # keep old samples strategy comes here
        data = newData

        # data preprocessors come here

        policyLearner.updateModel(newData)

        # FIXME currently not implemented
        #trial.store("avgReturns",np.mean(newData.getDataEntry("returns")), Experiments.StoringType.ACCUMULATE)

        print(
            "Iteration: %d, Episodes: %d, AvgReturn: %f\n" %
            (i,
             i *
             settings.numSamplesEpisodes,
             np.mean(
                 newData.getDataEntry('returns'))))
