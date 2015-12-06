'''
Created on 06.12.2015

@author: Moritz
'''


class Policy(object):
    '''
    Basic policy class, containing a policy function and a its corresponding sampler pool
    '''

    def __init__(self, policyFunction, poolName, policyName=None):
        '''
        Initialize the policy with a function and a corresponding pool

        @param policyFunction: The policy function to be executed
        @param poolName: The name of the pool to assign the sampler to when added to a sampler
        @param policyName: Unique policy name (default: 'sample'+poolName)
        '''

        self._policyFunction = policyFunction
        '''
        The policy function to be executed
        '''

        self._poolName = poolName
        '''
        The name of the pool to assign the sampler to when added to a sampler
        '''

        if policyName is None:
            policyName = 'sample' + poolName[0].upper() + poolName[1:]
        self._poolName = policyName
        '''
        Unique policy name
        '''
