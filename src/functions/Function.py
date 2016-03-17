from functions.MappingInterface import MappingInterface


class Function(MappingInterface):
    '''
    The Function class is the base class for every function.

    It registers the data manipulation function `getExpectation` and
    defines it as an abstract function to make sure every function implements
    that function.
    '''

    def Function():
        pass

    def registerMappingInterfaceFunction(self):
        if self.registerDataFunctions:
            self.addMappingFunction('getExpectation')

    def getExpectation(self, numElements, varargin):
        '''
        Returns the expectation of the Function.
        '''
        raise NotImplementedError()
