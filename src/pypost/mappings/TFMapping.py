import tensorflow as tf
from pypost.data.DataManipulator import DataManipulator
from pypost.mappings import Mapping
import pypost.common.tfutils as tfutils

class TFMapping(Mapping):

    @staticmethod
    def getTensorInputOutput(dataManager, tensorNode):
        if isinstance(tensorNode, (list, tuple)):
            placeHolderList = set()
            for tensor in tensorNode:
                if not isinstance(tensor, (tf.Tensor, tf.Variable)):
                    raise ValueError('TF Mappings can only be created for tf.Tensor objects or list/tuple of those')
                placeHolderList = placeHolderList | tfutils.list_data_placeholders(dataManager, tensor)
        elif isinstance(tensorNode, (tf.Tensor, tf.Variable)):
            placeHolderList = tfutils.list_data_placeholders(dataManager, tensorNode)
        else:
            raise ValueError('TF Mappings can only be created for tf.Tensor objects or list/tuple of those')
        inputVariables = []

        for placeHolder in placeHolderList:
            inputVariables.append(dataManager.getEntryForTensor(placeHolder))

        if isinstance(tensorNode, (list, tuple)):
            outputVariables = []
            tensorNodes = []
            tensorNodesEntry = []

            for tensor in tensorNode:
                if dataManager.isEntryTensor(tensor):
                    outputVariables.append(dataManager.getEntryForTensor(tensor))
                    tensorNodesEntry.append(tensor)
                else:
                    tensorNodes.append(tensor)

            tensorNode = tensorNodesEntry + tensorNodes

        else:
            if dataManager.isEntryTensor(tensorNode):
                outputVariables = dataManager.getEntryForTensor(tensorNode)
            else:
                outputVariables = []

        return inputVariables, outputVariables, placeHolderList, tensorNode

    @staticmethod
    def printTensorInputOutput(dataManager, tensorNode):
        inputVariables, outputVariables, *args = TFMapping.getTensorInputOutput(dataManager, tensorNode)
        print('{} -> {}'.format(inputVariables,outputVariables))

    def __init__(self, dataManager, tensorNode):

        inputVariables, outputVariables, placeHolderList, tensorNode = TFMapping.getTensorInputOutput(dataManager, tensorNode)

        Mapping.__init__(self, dataManager, inputVariables = inputVariables, outputVariables = outputVariables)
        self.inputTensors = placeHolderList
        self.outputTensors = tensorNode

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
