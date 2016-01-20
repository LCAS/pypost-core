'''
Created on 09.01.2016

@author: Moritz
'''
from interfaces import MappingInterface
from data import DataManager
from data import DataManipulator


class Mapping(MappingInterface, DataManipulator):
    '''
    The Mapping class is a DataManipulator that is able to combine a
    number of data manipulation functions.
    
    Every Mapping contains a set of data manipulation function as well as
    sets for the input and output variables. The input and output can be 
    defined in the constructor or at a later point via setInputVariables()
    and setOutputVariables(). New mapping functions have to be 
    added with the addMappingFunction()
    '''

    def __init__(
            self, dataManager, inputVariables=None, outputVariables=None, mappingName=""):
        '''
        Constructor
        @param dataManager: the data manager the mapping is operating on
        @param inputVariables: iterable of input variable names
        @param outputVariable: name of the output variable
        @param mappingName: name of the mapping

        @change: dataManager was removed from function arguments and is now a constructor argument.
        @change: registeredMappingFunctions was never used and got deleted
        @change registerDataFunctions is eqivalent to inputVariables = empty 
        #FIXME check registerDataFunctions invariant again, they are doing strange things ...
        '''
        
        MappingInterface.__init__(self)
        DataManipulator.__init__(self,dataManager)

        self.dataManager = dataManager
        '''
        The data manager the mapping is operating on
        '''
        
        self.mappingName = mappingName
        '''
        Name of the mapping function
        TODO change to property
        '''

        self.inputVariables = {}
        '''
        Input variables for mapping functions
        '''
        if inputVariables!=None:
            self.setInputVariables(inputVariables)
        
        self.additionalVariables = {}

        self.outputVariables = {}
        '''
        Output variables for mapping functions
        '''
        if outputVariables!=None:
            self.setOutputVariables(outputVariables)
        

        #self.dimInput = {}

        #self.dimOutput = {}

        self.mappingFunctions = {}

        self.mappingFunctionsOutputVars = {}

        

    def setAdditionalInputVariables(self, variables):
        self.additionalVariables.extend(variables)

    def addMappingFunction(self, function, outputVariables=None):
        '''
        @param function: the function to add to the mapping
        @param outputVariables new output variables. defaults to the Mapping output variables if not set
        
        By adding a new mapping function the Mapping will register 
        a new DataManipulationFunction in the DataManager, with 
        the currently defined inputVariables and the current set of
        outputVariables also including the new outputVariables added
        in this function call. (see also Data.DataManipulator)
        #FIXME see also DataManipulator -> DataManipulator has no addMappingFunction
        '''
        if outputVariables==None:
            outputVariables={}
        
        outputVariables.extend(self.outputVariables)
        
        self.mappingFunctions.append(function)
        self.mappingFunctionsOutputVariables.append(outputVariables)
                
            obj.mappingFunctions{end + 1} = mappingFunctionName;
            obj.mappingFunctionsOutputVariables{end + 1} = {};
            
            for i = 1:length(outputVariables)
                obj.mappingFunctionsOutputVariables{end}{i} = [obj.outputVariable, outputVariables{i}];
            end            
            

            if (~isempty(obj.inputVariables))
                if (~isnumeric(obj.inputVariables{1}))
                    
                                                    function,                  inputArguments,                                     outputArguments,                          callType, takesNumElements
                    obj.addDataManipulationFunction(obj.mappingFunctions{end}, [obj.inputVariables, obj.additionalInputVariables], obj.mappingFunctionsOutputVariables{end}, true,     true);
                end
            else
                obj.addDataManipulationFunction(obj.mappingFunctions{end}, [obj.additionalInputVariables], obj.mappingFunctionsOutputVariables{end}, true, true);
            end
            
        end
        
    def registerMappingFunction(self):
        for function in self.mappingFunctions:
            self.addDataManipulationFunction(function, )
            obj.addDataManipulationFunction(obj.mappingFunctions{i}, [obj.inputVariables, obj.additionalInputVariables{:}], [obj.outputVariables{1}, obj.mappingFunctionsOutputVariables{i}], true, true);
    
    def setInputVariables(self, inputVariables):
        self.inputVariables=inputVariables;
        
            if (~isempty(obj.inputVariables))
                if (~isnumeric(obj.inputVariables{1}))
                    obj.dimInput = self.dataManager.getNumDimensions(obj.inputVariables);
                    
                    if (isempty(obj.inputVariables) || isempty(obj.inputVariables{1}))
                        obj.inputVariables = {};
                    end

                    for i = 1:length(obj.mappingFunctions)
                        obj.setInputArguments(obj.mappingFunctions{i}, obj.inputVariables, obj.additionalInputVariables{:});
                    end
                else
                    obj.dimInput = obj.inputVariables{1};
                    obj.registerDataFunctions = false;
                end
            else
%                obj.registerDataFunctions = false;
%                obj.dimInput = obj.inputVariables{1};
                obj.dimInput = 0;
            end
        end
        
    def getInputVariable(self, index):
        return self.inputVariables[index]
        
    def setOutputVariables(self, outputArgument):
        
    
            if(isnumeric(outputArgument))
                obj.dimOutput = outputArgument;
                obj.outputVariable = {};

                if (obj.registerDataFunctions)
                    for i = 1:length(obj.mappingFunctions)
                        obj.setOutputArguments(obj.mappingFunctions{i}, [obj.mappingFunctionsOutputVariables{i}]);
                    end
                end
            else
                obj.outputVariable = outputArgument;
                
                obj.dimOutput = obj.dataManager.getNumDimensions(obj.outputVariable);
                
                for i = 1:length(obj.mappingFunctions)
                    obj.setOutputArguments(obj.mappingFunctions{i}, [outputArgument, obj.mappingFunctionsOutputVariables{i}]);
                end
            end            
        end
    
    def getOutputVariable(self):
        return self.outputVariable
        
        function [] = cloneDataManipulationFunctions(obj, cloneDataManipulator)
            obj.cloneDataManipulationFunctions@Data.DataManipulator(cloneDataManipulator);
            obj.inputVariables = cloneDataManipulator.inputVariables;
            obj.outputVariable = cloneDataManipulator.outputVariable;
            obj.dimInput = obj.dataManager.getNumDimensions(obj.inputVariables);
            obj.dimOutput = obj.dataManager.getNumDimensions(obj.outputVariable);
        end
    