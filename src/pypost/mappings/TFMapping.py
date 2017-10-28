import tensorflow as tf
from pypost.data.DataManipulator import DataManipulator
from pypost.mappings import Mapping
from pypost.mappings.Mapping import MappingMetaClass
import pypost.common.tfutils as tfutils


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

    def __call__(cls, *args, **kw):

        obj = type.__call__(cls, *args, **kw)
        obj.addTensorsForVariables()
        return obj

class TFMapping(Mapping, metaclass=TFMappingMetaClass):

    @staticmethod
    def TensorMethod(useAsMapping=False, connectTensorToOutput=False):
        def wrapper(function):
            function.isTensorFunction = True
            function.isMappingTensor = useAsMapping
            function.connectTensorToOutput = connectTensorToOutput
            return function

        return wrapper

    def __init__(self, dataManager, inputVariables=[], outputVariables=[], name = '', tensorNode = None):
        Mapping.__init__(self, dataManager, inputVariables = inputVariables, outputVariables = outputVariables, name = name)

        self.outputTensors = tensorNode

        self.inputTensors = []
        self._tensorFunctionsDict = {}

        if (self.outputTensors is not None):
            self.setMappingTensorNode(self.outputTensors)

        for tensorFunction in self.tensorFunctionsList:
            self._tensorFunctionsDict[tensorFunction] = None

        self._parameter_dict = {}
        self._variable_dict = {}

        self.tv_variables_list = []
        self._parameters_flat = None
        self._parameters_setter = None

        self._in_scope = False

        self.layers = []

    def _setLayersFromTensor(self, tensorNode):
        self.layers = tfutils._get_layers(tensorNode)

    def getNumLayers(self):
        return len(self.layers)

    def addTensorsForVariables(self):

        self.tv_variables_list = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope=self.name)

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

            setattr(self, name, None)
            setattr(self, name_var, None)

    def __setattr__(self, name, value):

        if (value is not None and name != '_parameter_dict' and hasattr(self, '_parameter_dict') and name in self._parameter_dict):
            return self._setTensorVariable(name, value)
        else:
            return super().__setattr__(name, value)

    def _setTensorVariable(self, name, value):

        assert name in self._parameter_dict, 'TF parameter %s unknown' % name

        if name == 'params':
            self._parameters_setter(value)
        else:
            tensor = self._parameter_dict[name]
            op = tensor.assign(value)
            tf.get_default_session().run(op)
        return value

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

        def gradient(variables=self.tv_variables_list):
            if (not isinstance(variables, list)):
                variables = [variables]
            return tfutils.flatgrad(tensor, variables)

        tensor.gradient = gradient
        self._tensorFunctionsDict[name] = tensor
        if (tensorFunction.connectTensorToOutput):
            self.dataManager.connectTensorToEntry(tensor, self.outputVariables[0])

    def __getattribute__(self, name):

        if (name == '_parameter_dict' or name == '_tensorFunctionsDict' or name == '_variable_dict'):
            return super().__getattribute__(name)

        if (hasattr(self, '_parameter_dict') and name in self._parameter_dict):
            return self._getTensorVariable(name)
        elif (hasattr(self, '_tensorFunctionsDict') and name in self._tensorFunctionsDict):
            if self._tensorFunctionsDict[name] == None:
                self._addTensorFunction(name)
            return self._tensorFunctionsDict[name]
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


    def setMappingTensorNode(self, tensorNode):
        inputVariables, outputVariables, placeHolderList, tensorNode = self.dataManager.getTensorInputOutput(tensorNode)
        self.setInputVariables(inputVariables)
        self.setOutputVariables(outputVariables)
        self.inputTensors = placeHolderList
        self.outputTensors = tensorNode

    def getAllInputTensor(self):

        inputTensors = []
        for input in self.inputVariables:
            inputTensors.append(self.dataManager.createTensorForEntry(input))

        allInputTensor = tf.concat(inputTensors, 1)
        return allInputTensor

    def getInputTensor(self, index):
        inputTensor = self.dataManager.createTensorForEntry(self.inputVariables[index])
        return inputTensor


    @Mapping.MappingMethod()
    def tensorFunction(self, *args):

        feedDict = dict(zip(self.inputTensors, args))
        results = tf.get_default_session().run(self.outputTensors, feed_dict=feedDict)

        return results



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
