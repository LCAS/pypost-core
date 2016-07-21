import numpy as np
from pypost.kernel.Kernel import Kernel


class ExponentialQuadraticKernel(Kernel):

    def __init__(self, normalized=False, **kwds):
        super().__init__(**kwds)

        self.ARD = True
        self.normalized = normalized

        if self.ARD:
            # Unique band width for every dimension of the states
            self.bandwidth = np.ones(self.numDims)
        else:
            self.bandwidth = 1

    def setBandwidth(self, bandwidth):
        if self.ARD:
            self.bandwidth = bandwidth
        else:
            self.bandwidth = np.mean(bandwidth)

        self._kernelTag += 1

    def getBandwidth(self):
        return self.bandwidth

    def getHyperParameters(self):
        return self.bandwidth

    def getNumHyperParameters(self):
        if self.ARD:
            return self.bandwidth.size
        else:
            return 1

    def setHyperParameters(self, bandwidth, **kwds):
        super().setHyperParameters(**kwds)

        if self.ARD:
            assert (bandwidth.ndim == 1)
            assert (bandwidth.shape[0] == self.numDims)
            self.bandwidth = bandwidth.flatten()
        else:
            assert np.isscalar(bandwidth)
            self.bandwidth = bandwidth

    def getGramMatrix(self, a, b):
        if np.isscalar(self.bandwidth):
            Q = np.eye(a.shape[1]) / (self.bandwidth ** 2)
        else:
            Q = np.diag((1 / (self.bandwidth ** 2)))

        aQ = a.dot(Q)

        aQ_a = np.sum(aQ * a, axis=1)

        bQ_b = np.sum(b.dot(Q) * b, axis=1)

        # Equivalent to MATLAB bsxfun(@plus, ..)
        sqdist = aQ_a[:, np.newaxis] + bQ_b - 2 * aQ.dot(b.T)

        K = np.exp(-0.5 * sqdist)

        if self.normalized:
            K = K / np.sqrt((self.bandwidth**2).prod() * (2*np.pi)**a.shape[1])

        return K

    def getGramDiag(self, data):
        return np.ones((data.shape[0], 1))

    def getKernelDerivParam(self, data):
        gramMatrix = self.getGramMatrix(data, data)
        gradientMatrices = np.zeros([self.getNumHyperParameters(),
                                     np.size(gramMatrix, axis=0),
                                     np.size(gramMatrix, axis=1)])

        if self.normalized:
            assert False, 'Derivative not implemented for normalized kernel'

        if self.ARD:
            for dim in range(0, self.num_dims):
                sqdist = ((data[:, dim])[:, np.newaxis] - data[:, dim]) ** 2
                gradientMatrices[dim, :, :] = -gramMatrix * \
                    (sqdist.dot(1 / (self.bandwidth[dim] ** 3)))
        else:
            sum_el = np.sum(data * data, axis=1)
            sqdist = (sum_el[:, np.newaxis] + sum_el) - (2 * data.dot(data.T))
            gradientMatrices[0, :, :] = -gramMatrix * \
                (sqdist.dot(1 / (self.bandwidth[0] ** 3)))

        gradientMatrices = -gradientMatrices

        return gradientMatrices, gramMatrix

    def getKernelDerivData(self, ref_data, cur_data):
        pass
