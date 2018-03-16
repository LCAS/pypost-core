from pypost.data import DataManager
import pypost.common.tfutils as tfutils
import tensorflow as tf
import numpy as np
from pypost.mappings import TFMapping

num_cpu = 1
tf_config = tf.ConfigProto(inter_op_parallelism_threads=num_cpu, intra_op_parallelism_threads=num_cpu)
session = tf.Session(config=tf_config)
session.__enter__()


#define our mapping class. A mapping is a callable object, where the call function is implemented by the MappingMethod decorator

# Create a dataManager that can handle the input (X) and output (Y) of a 1 dimensional
# function
dataManager = DataManager('values')
dataManager.addDataEntry('X', 2)
dataManager.addDataEntry('Y', 2)
dataManager.addDataEntry('Z', 2)

x = dataManager.createTensorForEntry('X')
y = dataManager.createTensorForEntry('Y')

data = dataManager.createDataObject([10])

data[...].X = np.ones((10,2))
data[...].Y = np.ones((10,2))

z = x + y
y1 = x - z

dataManager.connectTensorToEntry(z, 'Z')
dataManager.connectTensorToEntry(y1, 'Y')

data[...] >> (z, y1) >> data

print(data[...].Y)

print(data[...].Z)

dataManager.printTensorInputOutput(y1)

output = tfutils.create_layers_linear_ouput(x, [100,100], 10)
tfutils.initialize()

tfutils.list_trainable_variables(output)

import pickle
stringDump = pickle.dumps(dataManager)
dataManager1 = pickle.loads(stringDump)

stringDump = pickle.dumps(dataManager)
