import numpy as np
import sys

# Relative Entropy Policy Search (REPS) Dual Function
# used as Benchmark
def dualFunction(params, repsData):

    phiMat = repsData['stateFeatures'][0][0]
    phiHat = repsData['meanStateFeatures'][0][0]
    R = repsData['rewards'][0][0]
    importanceWeights = repsData['sampleWeighting'][0][0]
    # make entirely sure nothing gets overwritten
    phiMat.flags.writeable = False
    phiHat.flags.writeable = False
    R.flags.writeable = False
    importanceWeights.flags.writeable = False

    epsilon = 0.2

    numFeatures = np.shape(phiMat)[1]
    theta = np.squeeze(params[:numFeatures])
    eta = np.squeeze(params[numFeatures:])

    if len(theta) != 0:
        V    = np.reshape(np.dot(phiMat, theta), (-1, 1))
        VHat = np.dot(phiHat, theta)
    else:
        V    = 0
        VHat = 0

    advantage = R - V
    maxAdvantage = np.max(advantage)
    R2 = R - maxAdvantage
    advantage  = (R2-V) / eta
    boundedAdvantage = advantage

    gD = np.zeros(np.shape(params))

    if np.max(boundedAdvantage) > 500:
        g = 1e30 - eta
        gD[-1] = -1
        return g, gD

    N = np.sum(importanceWeights)
    expAdvantage = importanceWeights * np.exp(boundedAdvantage)
    sumExpAdvantage = np.sum(expAdvantage)

    realmin = sys.float_info.min
    if sumExpAdvantage < realmin:
        sumExpAdvantage = realmin
    if N < realmin:
        N = realmin

    gLogPart = 1 / N * sumExpAdvantage

    g = eta * np.log(gLogPart) + VHat + maxAdvantage
    g += eta * epsilon

    gDEta = epsilon + np.log(gLogPart) - np.sum(expAdvantage * (R2-V)) / (eta * sumExpAdvantage)
    if (eta * sumExpAdvantage) == 0:
        gDEta = 1e100
    gD[numFeatures:] = gDEta

    gdTheta = phiHat - np.sum(phiMat * expAdvantage, 0) / sumExpAdvantage
    gD[:numFeatures] = np.squeeze(gdTheta)

    if np.isnan(g) :#or np.isnan(any(gD)):
        print('NAN in value function or gradient!')

    return g[0], gD