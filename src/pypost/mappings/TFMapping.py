import tensorflow as tf
import numpy as np

import pypost.common.tfutils as tfutils
from pypost.mappings import Mapping
from pypost.mappings.DataManipulator import CallType
from pypost.mappings.DataManipulator import DataManipulator
from pypost.mappings.Mapping import MappingMetaClass


class TFMappingMetaClass(MappingMetaClass):
    def __init__(cls, name, bases, dct):

        super(TFMappingMetaClass, cls).__init__(name, bases, dct)

        cloneDict = cls.__dict__.copy()
        if (hasattr(cls.__base__, 'tensorFunctionsList')):
            cls.tensorFunctionsList = cls.__base__.tensorFunctionsList.copy()
        else:
            cls.tensorFunctionsList = []
        for (key, function) in cloneDict.items():

            if (hasattr(function, '__name__')):
                name = function.__name__

                if (hasattr(function, 'isTensorFunction') and  function.isTensorFunction):
                    setattr(cls, name, None)
                    setattr(cls, 'tm_' + name, function)
                    cls.tensorFunctionsList.append(name)

                    if (function.isMappingTensor):
                        cls.callTensor = name
                        cls.callFunctionName = 'tensorFunction'

                        callFunction = getattr(cls, cls.callFunctionName)
                        setattr(cls, '__call__', callFunction)

    def __call__(cls, *args, **kw):

        obj = type.__call__(cls, *args, **kw)
        obj._addAllTensorFunctions()
        obj.addTensorsForVariables()
        if cls.callTensor:
            obj._setMappingTensorNode(getattr(obj,'tn_' + cls.callTensor))

        tfutils.initialize()
        obj.initialize_params()


        if not isinstance(obj.outputTensors, list):
            if (hasattr(obj.outputTensors, 'callType')):
                obj.tensorFunction.dataFunctionDecorator.callType = obj.outputTensors.callType
                obj.dataFunctionDecorator.callType = obj.outputTensors.callType

        else:
            if any([hasattr(outTensor, 'callType') and outTensor.callType == CallType.SINGLE_SAMPLE for outTensor in obj.outputTensors]):
                obj.tensorFunction.dataFunctionDecorator.callType = CallType.SINGLE_SAMPLE
                obj.dataFunctionDecorator.callType = CallType.SINGLE_SAMPLE
        return obj

class TFMapping(Mapping, metaclass=TFMappingMetaClass):

    callTensor = None

    @staticmethod
    def TensorMethod(useAsMapping=False, additionalInputTensors = None, connectTensorToOutput=None, callType = CallType.ALL_AT_ONCE):
        def wrapper(function):
            function.isTensorFunction = True
            function.isMappingTensor = useAsMapping
            function.connectTensorToOutput = connectTensorToOutput
            function.callType = callType
            
            function.additionalInputTensors = additionalInputTensors
            function.additionalFeedDict = {}
            
            return function

        return wrapper


    def __init__(self, dataManager, inputVariables=[], outputVariables=[], name = '', tensorNode = None):

        if (isinstance(inputVariables, (tf.Tensor, tf.Variable))):
            inputTensor = inputVariables
            inputVariables = []
        else:
            inputTensor = None


        Mapping.__init__(self, dataManager, inputVariables = inputVariables, outputVariables = outputVariables, name = name)

        self.outputTensors = tensorNode

        self.inputTensorsEntry = []
        self.inputTensorsProperty = []

        self.inputProperties = []
        self.inputTensor = inputTensor

        self._tensorFunctionsDict = {}
        self._tensorNodeDict = {}

        if (self.outputTensors is not None):
            self._setMappingTensorNode(self.outputTensors)

        for tensorFunction in self.tensorFunctionsList:
            self._tensorFunctionsDict[tensorFunction] = None
            self._tensorNodeDict['tn_' + tensorFunction] = None

        self._parameter_dict = {}
        self._parameter_placeholder = {}
        self._parameter_settensor = {}
        self._variable_dict = {}
        self._dataPropertiesTensors = []


        self.tv_variables_list = []
        self._parameters_flat = None
        self._parameters_setter = None

        self._in_scope = False
        self.additionalScopes = []

        self.layers = []
        self.isTensorNodeSet = False
        self.useEmpty = False
        if (tensorNode is not None):
            self._setMappingTensorNode(tensorNode)

    def initialize_params(self):
        return

    def tensor(self):
        return self.outputTensors

    def _setLayersFromTensor(self, tensorNode):
        self.layers = tfutils._get_layers(tensorNode)

    def getNumLayers(self):
        return len(self.layers)

    def addTensorsForVariables(self):

        self.tv_variables_list = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=self.name)

        for scopeNames in self.additionalScopes:
            self.tv_variables_list = self.tv_variables_list + tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=scopeNames)


        if len(self.tv_variables_list) > 0:
            self._addTensorVariables(self.tv_variables_list)

            self._parameters_flat = tf.concat(axis=0, values=[tf.reshape(v, [tfutils.numel(v)]) for v in self.tv_variables_list])

            self._parameter_dict['params'] = self._parameters_flat

            setattr(self, 'params', None)

            self._parameters_setter = tfutils.SetFromFlat(self.tv_variables_list)

    def listTFVariables(self):
        print(self._parameter_dict.keys())

    def _addTensorVariables(self, tensor_list):

        if not isinstance(tensor_list, list):
            tensor_list = [tensor_list]

        for tensor in tensor_list:
            name = tensor.name[:-2]
            index = name.rfind("/")
            if  index >= 0:
                name = name[index + 1:]

            name_var = 'tv_' + name
            name = 'param_' + name

            self._parameter_dict[name] = tensor
            self._variable_dict[name_var] = tensor

            placeHolder = tf.placeholder(dtype=tf.float32, shape = tensor.shape.as_list())
            self._parameter_placeholder[name] = placeHolder
            self._parameter_settensor[name] = tensor.assign(placeHolder)

            setattr(self, name, None)
            setattr(self, name_var, None)

    def __setattr__(self, name, value):

        if (value is not None and name != '_parameter_dict' and hasattr(self, '_parameter_dict') and name in self._parameter_dict):
            return self._setTensorVariable(name, value)
        else:
            #if not hasattr(self, name):
            #    raise ValueError('AttributeError: \'{}\' object has no attribute \'{}\''.format(self.__class__.name, name))

            return super().__setattr__(name, value)

    def _setTensorVariable(self, name, value):

        assert name in self._parameter_dict, 'TF parameter %s unknown' % name

        if name == 'params':
            self._parameters_setter(value)
        else:
            tensor = self._parameter_dict[name]

            desShape = tensor.shape.as_list()

            #if (isinstance(value, np.ndarray)):
            #    if ()
            #    if (len(desShape) > len(value.shape)):


            if isinstance(value, (float, int)):
                value = np.ones(tuple(tensor.shape.as_list())) * value

            tf.get_default_session().run(self._parameter_settensor[name], {self._parameter_placeholder[name] : value})
        return value

    def _addAllTensorFunctions(self):
        for name in self._tensorFunctionsDict.keys():
            if self._tensorFunctionsDict[name] == None:
                self._addTensorFunction(name)

    def _preprocessTensor(self, tensor):

        #TODO: preprocess additional Input Tensors (evaluate)

        if (hasattr(tensor, 'preprocessed')) and tensor.preprocessed:
            tensorMapping = TFMapping(self.dataManager, tensorNode=tensor)

            return tensorMapping

        if (hasattr(tensor, 'addtionalInputTensors')):
            tensor.additionalInputTensors = [eval(tensorName) for tensorName in tensor.additionalInputTensors]
        else:
            tensor.additionalInputTensors = []

        def gradient(variables=None):
            if (variables == None):
                variables = self.tv_variables_list

            if (not isinstance(variables, list)):
                variables = [variables]
            return tfutils.flatgrad(tensor, variables)

        def single_gradient(variables=None):
            if (variables == None):
                variables = self.tv_variables_list
            if (not isinstance(variables, list)):
                variables = [variables]
            gradientTensor = tfutils.flatgrad(tensor, variables)
            gradientTensor.callType = CallType.SINGLE_SAMPLE
            return gradientTensor
        
        def additional_inputs(*argc):
            assert(len(argc) <= len(tensor.additionalInputTensors))
            #TODO: Make dictionary out of tensor.additionalInputTensors and argc
            # put in tensor.additionalFeedDict
            return tensor

        tensor.gradient = gradient
        tensor.single_gradient = single_gradient
        tensor.preprocessed = True

        tensorMapping = TFMapping(self.dataManager, tensorNode=tensor)

        return tensorMapping

    def _addTensorFunction(self, name):
        tensorFunction = getattr(self, 'tm_' + name)

        if (self._in_scope):
            tensor = tensorFunction()
        else:
            with tf.variable_scope(self.name):
                with tf.name_scope(self.name):
                    self._in_scope = True
                    tensor = tensorFunction()
                    self._in_scope = False

        tensor.callType = tensorFunction.callType

        if (tensorFunction.connectTensorToOutput):
            if (isinstance(tensorFunction.connectTensorToOutput, bool)):
                self.dataManager.connectTensorToEntry(tensor, self.outputVariables[0])
            elif isinstance(tensorFunction.connectTensorToOutput, string):
                if (tensorFunction.connectTensorToOutput.startsWith('self.')):
                    outEntry = eval(tensorFunction.connectTensorToOutput)
                    self.dataManager.connectTensorToEntry(tensor, outEntry)
                else:
                    self.dataManager.connectTensorToEntry(tensor, tensorFunction.connectTensorToOutput)

        tensorMapping = self._preprocessTensor(tensor)
        self._tensorFunctionsDict[name] = tensorMapping
        self._tensorNodeDict['tn_' + name] = tensorMapping.tensor()


    def __getattribute__(self, name):

        if (name == '_parameter_dict' or name == '_tensorFunctionsDict' or name == '_variable_dict' or name == '_tensorNodeDict'):
            return super().__getattribute__(name)

        if (hasattr(self, '_parameter_dict') and name in self._parameter_dict):
            return self._getTensorVariable(name)
        elif (hasattr(self, '_tensorFunctionsDict') and name in self._tensorFunctionsDict):
            if self._tensorFunctionsDict[name] == None:
                self._addTensorFunction(name)
            return self._tensorFunctionsDict[name]
        elif (hasattr(self, '_tensorNodeDict') and name in self._tensorNodeDict):
            #remove 'tn_' prefix
            nameNode = name[3:]

            if self._tensorFunctionsDict[nameNode] == None:
                self._addTensorFunction(nameNode)
            return self._tensorNodeDict[name]

        elif (hasattr(self, '_variable_dict') and name in self._variable_dict):
            return self._variable_dict[name]
        else:
            return super().__getattribute__(name)

    def _getTensorVariable(self, name):

        assert name in self._parameter_dict, 'TF parameter %s unknown' % name

        if name == 'params':
            tensor = self._parameters_flat
        else:
            tensor = self._parameter_dict[name]
        return tensor.eval()

    def getParamsFlatTensor(self):
        return self._parameters_flat

    def _setMappingTensorNode(self, tensorNode):
        inputVariables, outputVariables, placeHolderList, tensorNode = self.dataManager.getTensorInputOutput(tensorNode)

        self.inputVariables = []
        self.inputProperties = []
        self.inputTensorsEntry = []
        self.inputTensorsProperty = []

        for i in range(0, len(placeHolderList)):
            if hasattr(placeHolderList[i], 'propertyObject'):
                self.inputProperties.append(inputVariables[i])
                self.inputTensorsProperty.append(placeHolderList[i])
            else:
                self.inputVariables.append(inputVariables[i])
                self.inputTensorsEntry.append(placeHolderList[i])

        self.setInputVariables(self.inputVariables)
        self.setOutputVariables(outputVariables)
        self.outputTensors = tensorNode
        self.isTensorNodeSet = True

    def getAllInputTensor(self):

        if (self.inputTensor is not None):
            return self.inputTensor
        else:
            inputTensors = []
            for input in self.inputVariables:
                inputTensors.append(self.dataManager.createTensorForEntry(input))

            if len(inputTensors) > 0:
                allInputTensor = tf.concat(inputTensors, 1)
                self.useEmpty = False
            else:
                allInputTensor = self.dataManager.createTensorForEntry('empty')
                self.useEmpty = True

            return allInputTensor

    def getInputTensorIndex(self, index):
        inputTensor = self.dataManager.createTensorForEntry(self.inputVariables[index])
        return inputTensor

    def getInputTensorName(self, name):
        tensor =  self.dataManager.createTensorForEntry(name)
        if (name in self._dataProperties and not tensor in self._dataPropertiesTensors):
            self._dataPropertiesTensors.append(tensor)
            tensor.propertyObject = self
            tensor.propertyName = name

        return tensor


    @Mapping.MappingMethod()
    def tensorFunction(self, *args):
        if (not self.isTensorNodeSet):
            raise ValueError('TFMapping has not been correctly intialized. No TensorMethod was indicated for the Mapping. '
                             'Use property useAsMapping = True for exactly one TensorMethod.')

        if len(args) == 0 and len(self.inputVariables) == 1 and self.inputVariables[0] == 'empty':
            args = [np.zeros((1,0))]

        if len(args) != len(self.inputVariables):
            raise ValueError(
                'Error calling tensor method. Please provide the correct number of inputs as given in .inputVariables!')

        newArgs = []

        singleSample = False
        oneDArray = False
        scalarValue = False

        args = list(args)
        for tensorProperty in self.inputTensorsProperty:
            args.append(getattr(tensorProperty.propertyObject, tensorProperty.propertyName))

        for i in range(0, len(args)):
            if (not isinstance(args[i], np.ndarray)):
                newArgs.append(np.array([[args[i]]]))
                scalarValue = True
            elif len(args[i].shape) == 1:
                if (self.dataManager.getNumDimensions(self.inputVariables[i]) == 1):
                    newArgs.append(args[i].reshape((args[i].shape[0],1)))
                    oneDArray = True
                else:
                    newArgs.append(args[i].reshape((1, args[i].shape[0])))
                    singleSample = True
            else:
                newArgs.append(args[i])


        feedDict = dict(zip(self.inputTensorsEntry + self.inputTensorsProperty, newArgs))
        results = tf.get_default_session().run(self.outputTensors, feed_dict=feedDict)

        def convertResults(resultItem):
            if not isinstance(resultItem, np.ndarray):
                return resultItem
            if (resultItem.shape[0] == 1):
                if len(resultItem.shape) == 1:
                    return resultItem[0]
                else:
                    if (resultItem.shape[1] == 1 and scalarValue):
                        return resultItem[0,0]
                    elif singleSample:
                        return resultItem.reshape((resultItem.shape[1],))
                    else:
                        return resultItem.transpose()
            elif len(resultItem.shape) > 1 and resultItem.shape[1] == 1 and oneDArray:
                return resultItem.reshape((resultItem.shape[0],))
            else:
                return resultItem

        if not isinstance(results, (list, tuple)):
            return convertResults(results)
        else:
            return tuple([convertResults(resultItem) for resultItem in results])

    @DataManipulator.DataMethod(inputArguments='self.inputVariables', outputArguments='self.outputVariables')
    def tensorFunctionPlain(self, *args):
        if (not self.isTensorNodeSet):
            raise ValueError(
                'TFMapping has not been correctly intialized. No TensorMethod was indicated for the Mapping. '
                'Use property useAsMapping = True for exactly one TensorMethod.')

        feedDict = dict(zip(self.inputTensorsEntry + self.inputTensorsProperty, args))
        results = tf.get_default_session().run(self.outputTensors, feed_dict=feedDict)

#
#
# class TFObject(DataManipulator):
#
#
#     def __init__(self, dataManager):
#         DataManipulator.__init__(dataManager)
#         self.placeHolderDict = {}
#         self.tensorDict = {}
#
#     def registerPlaceHolder(self, placeHolder):
#         self.placeHolderDict[placeHolder.name] = placeHolder
#
#     def getPlaceHolder(self, placeHolderName):
#         return self.placeHolderDict[placeHolderName]
#
#     def registerTensor(self, tensor, name):
#         self.tensorDict[name] = tensor
#
#     def isTensor(self, tensorName):
#         return tensorName in self.tensorDict
#
#     def getTensor(self, tensorName):
#         return self.tensorDict[tensorName]
#
#     @classmethod
#     def TFFunction(cls, inputTensors):
#         def decorate(function):
#
#             def newFunction(self, *args):
#                 if not self.isTensor('__' + function.name):
#                     if (isinstance(inputTensors, list)):
#                         placeHolders = [self.getPlaceHolder(item) for item in inputTensors]
#                     else:
#                         placeHolders = self.getPlaceHolder(inputTensors)
#
#                     tensor = function(self, placeHolders)
#                     self.registerTensor(tensor, '__' + function.__name__)
#                 else:
#                     tensor = self.getTensor('__' + function.__name__)
#
#
#                 if not hasattr(function, 'tensor'):
#
#             function.dataFunctionDecorator = DataManipulationFunction(function.__name__, inputArguments,
#                                                                       outputArguments,
#                                                                       callType, takesNumElements, takesData,
#                                                                       lazyEvaluation)
#             function.isMappingFunction = True
#             return function
#
#         return wrapper
