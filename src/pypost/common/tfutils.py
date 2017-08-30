import tensorflow as tf
import numpy as np

def _list_trainable_variables(tensor_node):
    if (isinstance(tensor_node, list)):
        place_set = set()
        for tfNode in tensor_node:
            place_set = place_set.union(_list_trainable_variables(tfNode))
        return place_set
    else:
        place_set = set()
        for tfNode in tensor_node.op.inputs:
            if tfNode.op.type.startswith('Variable'):
                place_set.add(tfNode)
            else:
                place_set = place_set.union(_list_trainable_variables(tfNode))
        return place_set

def list_trainable_variables(tensor_node):
    train_var = list(_list_trainable_variables(tensor_node))
    def get_name(tensor):
        return tensor.name
    train_var.sort(key=get_name)
    return train_var


def list_data_placeholders(dataManager, tensor_node):
    place_set = set()
    for tfNode in tensor_node.op.inputs:
        if tfNode.op.type == 'Placeholder' and dataManager.isEntryTensor(tfNode):
            place_set.add(tfNode)
        else:
            place_set = place_set.union(list_data_placeholders(dataManager, tfNode))
    return place_set

def normc_initializer(std=1.0):
    def _initializer(shape, dtype=None, partition_info=None):  # pylint: disable=W0613
        out = np.random.randn(*shape).astype(np.float32)
        out *= std / np.sqrt(np.square(out).sum(axis=0, keepdims=True))
        return tf.constant(out)
    return _initializer

def dense(x, size, name, weight_init=None, bias=True):
    w = tf.get_variable(name + "w", [x.get_shape()[1], size], initializer=weight_init)
    ret = tf.matmul(x, w)

    if bias:
        b = tf.get_variable(name + "b", [size], initializer=tf.zeros_initializer())
        return ret + b
    else:
        return ret

def create_layers(inputTensor, name, hiddenNodes):
    last_out = inputTensor
    for i in range(len(hiddenNodes)):
        last_out = tf.nn.tanh(dense(last_out, hiddenNodes[i], name + '__layer%d_' % (i + 1), weight_init = normc_initializer(1.0)))
    return last_out

def create_layers_linear_ouput(inputTensor, name, hiddenNodes, outputNodes):
    last_out = create_layers(inputTensor=inputTensor, name=name, hiddenNodes=hiddenNodes)
    last_out = dense(last_out, outputNodes, name + '__final_', weight_init=normc_initializer(0.01))
    return last_out

###### Initializer

ALREADY_INITIALIZED = set()

def initialize():
    """Initialize all the uninitialized variables in the global scope."""
    new_variables = set(tf.global_variables()) - ALREADY_INITIALIZED
    tf.get_default_session().run(tf.variables_initializer(new_variables))
    ALREADY_INITIALIZED.update(new_variables)


###### MLP generators

def continuous_MLP_generator(hiddenNodes):
    def generate(inputTensor, dimOutput, name):
        return create_layers_linear_ouput(inputTensor, name, hiddenNodes, dimOutput)
    return generate

def diagional_log_std_generator():
    def generate(inputTensor, dimOutput, name):
        return tf.get_variable(name=name + "__logstd", shape=[1, dimOutput], initializer=tf.zeros_initializer())
    return generate

###### Flatten vectors

def var_shape(x):
    out = x.get_shape().as_list()
    assert all(isinstance(a, int) for a in out), \
        "shape function assumes that shape is fully known"
    return out


def numel(x):
    return intprod(var_shape(x))


def intprod(x):
    return int(np.prod(x))

class SetFromFlat(object):
    def __init__(self, var_list, dtype=tf.float32):
        assigns = []
        shapes = list(map(var_shape, var_list))
        total_size = np.sum([intprod(shape) for shape in shapes])

        self.theta = theta = tf.placeholder(dtype, [total_size])
        start = 0
        assigns = []
        for (shape, v) in zip(shapes, var_list):
            size = intprod(shape)
            assigns.append(tf.assign(v, tf.reshape(theta[start:start + size], shape)))
            start += size
        self.op = tf.group(*assigns)

    def __call__(self, theta):
        tf.get_default_session().run(self.op, feed_dict={self.theta: theta})




class GetFlat(object):
    def __init__(self, var_list):
        self.op = tf.concat(axis=0, values=[tf.reshape(v, [numel(v)]) for v in var_list])

    def __call__(self):
        return tf.get_default_session().run(self.op)

###### TensorFlow Decorator

def tensor(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate
