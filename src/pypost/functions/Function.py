from pypost.functions.Mapping import Mapping


class Function(Mapping):
    '''
    The Function class is the base class for every function.

    It registers the data manipulation function `getExpectation` and
    defines it as an abstract function to make sure every function implements
    that function.
    '''

    def __init__(self, dataManager, inputVariables=None, outputVariables=None,
                 name=""):
        Mapping.__init__(self, dataManager, inputVariables, outputVariables, name)

    @Mapping.DataMappingFunction()
    def computeOutput(self, *args):
        '''
        Returns the expectation of the Function.
        '''
        raise NotImplementedError()
