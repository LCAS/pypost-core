class Policy(object):
    '''
    Basic policy class, containing a policy function and a its corresponding sampler pool
    '''

    def __init__(self, policyFunction, poolName, policyName=None):
        '''
        Initialize the policy with a function and a corresponding pool

        :param policyFunction: The policy function to be executed
        :param poolName: The name of the pool to assign the sampler to when added to a sampler
        :param policyName: Unique policy name (default: 'sample'+poolName)
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
        self._policyName = policyName
        '''
        Unique policy name
        '''

    def getPolicyFunction(self):
        return self._policyFunction

    def getPolicyName(self):
        return self._policyName

    def getPoolName(self):
        return self._poolName

    def __call__(self, *args, **kw):
        '''
        Execute the policy function and get the computed result.
        Always use this method to execute the policy function and do not
        call the stored policy function itself, as the internal structure may
        perform additional actions!
        '''
        return self.getPolicyFunction()(*args, **kw)
