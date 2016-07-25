import numpy as np

def boundCovariance(Sigma, minCov, minCorr):

    if (minCov.shape[0] > 0):
        for d in range(0, Sigma.shape[0]):

            if  np.isnan(Sigma[d, d]):
                Sigma[d, d] = minCov[d]

            scaling = max(minCov[d] / Sigma[d, d], 1)

            if not np.isinf(scaling):
                Sigma[:, d] = Sigma[:, d] * np.sqrt(scaling)
                Sigma[d, :] = Sigma[d, :] * np.sqrt(scaling)

                if minCorr < 1:
                    for r in range(0, Sigma.shape[0]):
                        if d != r:
                            # limit corrCoeff
                            corrCoeff = Sigma[d, r] / np.sqrt(Sigma[r, r] * Sigma[d, d])
                            if not np.isnan(corrCoeff) and np.abs(corrCoeff) > minCorr:
                                Sigma[d, r] = np.sign(corrCoeff) * minCorr * np.sqrt(Sigma[r, r] * Sigma[d, d])
                                Sigma[r, d] = Sigma(d, r)
            else:
                Sigma[d, d] = minCov[d]

            if Sigma[d, d] < minCov[d]:
                Sigma[d, d] = Sigma[d, d] + minCov[d]

    Sigma = (Sigma + Sigma.transpose()) / 2

    D, V = np.linalg.eig(Sigma)
    D[D < 0] = 0

    Sigma = np.dot(V, np.dot( np.diag(D), V.transpose()))

    return Sigma

def regularizeCovariance(Sigma, priorCov, numEffectiveSamples, priorCovWeight):

    count = 1

    while (count < 100):

        Sigma_temp = (Sigma * numEffectiveSamples + priorCov * priorCovWeight) / (numEffectiveSamples + priorCovWeight)

        priorCovWeight = priorCovWeight * 2
        count = count + 1

        try:
            cholSigma = np.linalg.cholesky(Sigma_temp).transpose()
            eigVal = np.diagonal(cholSigma)
            if np.isreal(cholSigma).all() and all(np.isreal(eigVal)) and all(eigVal.real > 0):
                return (Sigma_temp, cholSigma)

        except np.linalg.LinAlgError:
            pass

    raise Exception('pst::toolbox', 'Could not find decomposition for covariance matrix... HELP!!!')
