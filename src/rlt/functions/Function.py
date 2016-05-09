from rlt.functions.MappingInterface import MappingInterface


class Function(MappingInterface):
    '''
    The Function class is the base class for every function.

    It registers the data manipulation function `getExpectation` and
    defines it as an abstract function to make sure every function implements
    that function.
    '''

    def __init__(self):
        MappingInterface.__init__(self)
        self.registerDataFunctions = True
        pass

    def registerMappingInterfaceFunction(self):
        if self.registerDataFunctions:
            self.addMappingFunction(self.getExpectation)
        else:
            print("WARNING: registerDataFunctions is False")

    def getExpectation(self, numElements, *args):
        '''
        Returns the expectation of the Function.
        '''
        raise NotImplementedError()