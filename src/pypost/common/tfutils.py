import tensorflow as tf
import numpy as np

def sum(x, axis=None, keepdims=False):
    axis = None if axis is None else [axis]
    return tf.reduce_sum(x, axis=axis, keep_dims=keepdims)


def mean(x, axis=None, keepdims=False):
    axis = None if axis is None else [axis]
    return tf.reduce_mean(x, axis=axis, keep_dims=keepdims)


def var(x, axis=None, keepdims=False):
    meanx = mean(x, axis=axis, keepdims=keepdims)
    return mean(tf.square(x - meanx), axis=axis, keepdims=keepdims)


def std(x, axis=None, keepdims=False):
    return tf.sqrt(var(x, axis=axis, keepdims=keepdims))


def max(x, axis=None, keepdims=False):
    axis = None if axis is None else [axis]
    return tf.reduce_max(x, axis=axis, keep_dims=keepdims)


def min(x, axis=None, keepdims=False):
    axis = None if axis is None else [axis]
    return tf.reduce_min(x, axis=axis, keep_dims=keepdims)


def concatenate(arrs, axis=0):
    return tf.concat(axis=axis, values=arrs)


def argmax(x, axis=None):
    return tf.argmax(x, axis=axis)


def switch(condition, then_expression, else_expression):
    """Switches between two operations depending on a scalar value (int or bool).
    Note that both `then_expression` and `else_expression`
    should be symbolic tensors of the *same shape*.

    # Arguments
        condition: scalar tensor.
        then_expression: TensorFlow operation.
        else_expression: TensorFlow operation.
    """
    x_shape = then_expression.get_shape().copy()
    x = tf.cond(tf.cast(condition, 'bool'),
                lambda: then_expression,
                lambda: else_expression)
    x.set_shape(x_shape)
    return x

### Utilities for parsing tensors

def _list_trainable_variables(tensor_node):
    if (isinstance(tensor_node, list)):
        place_set = set()
        for tfNode in tensor_node:
            place_set = place_set.union(_list_trainable_variables(tfNode))
        return place_set
    elif tensor_node.op.type.startswith('Variable'):
        return set([tensor_node])
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

def _get_layers(tensor_node):
    layerList = []

    for tfNode in tensor_node.op.inputs:
        layerList = layerList + _get_layers(tfNode)

    name = tensor_node.name[:-2]
    if name.endswith('_out'):
        layerList.append(tensor_node)
    return layerList



def list_data_placeholders(dataManager, tensor_node):
    place_set = set()
    if (isinstance(tensor_node, (tf.Tensor, tf.Variable))):
        for tfNode in tensor_node.op.inputs:
            if tfNode.op.type == 'Placeholder' and dataManager.isEntryTensor(tfNode):
                place_set.add(tfNode)
            else:
                place_set = place_set.union(list_data_placeholders(dataManager, tfNode))

    else:
        # its an operation

        for tfNode in tensor_node._control_inputs:
            place_set = place_set.union(list_data_placeholders(dataManager, tfNode))

        for tfNode in tensor_node.inputs:
            if tfNode.op.type == 'Placeholder' and dataManager.isEntryTensor(tfNode):
                place_set.add(tfNode)
            else:
                place_set = place_set.union(list_data_placeholders(dataManager, tfNode))


    return place_set

### create layer functions

def normc_initializer(std=1.0):
    def _initializer(shape, dtype=None, partition_info=None):  # pylint: disable=W0613
        out = np.random.randn(*shape).astype(np.float32)
        out *= std / np.sqrt(np.square(out).sum(axis=0, keepdims=True))
        return tf.constant(out)
    return _initializer

def dense(x, size, name, weight_init=None, bias=True):

    if (x is not None):
        w = tf.get_variable(name + "w", [x.get_shape()[1], size], initializer=weight_init)
        ret = tf.matmul(x, w)
    else:
        ret = 0

    if bias:
        b = tf.get_variable(name + "b", [size], initializer=tf.zeros_initializer())
        return ret + b
    else:
        return ret

def create_layers(inputTensor, hiddenNodes):
    last_out = inputTensor
    for i in range(len(hiddenNodes)):
        last_out = tf.nn.tanh(dense(last_out, hiddenNodes[i], 'layer%d_' % (i + 1), weight_init = normc_initializer(1.0)), name = 'layer%d_out' % (i + 1))
    return last_out

def create_layers_linear_ouput(inputTensor, hiddenNodes, outputNodes):
    last_out = create_layers(inputTensor=inputTensor, hiddenNodes=hiddenNodes)
    last_out = dense(last_out, outputNodes, 'final_', weight_init=normc_initializer(0.01))
    return last_out

def create_linear_layer(inputTensor, outputNodes, useBias):
    last_out = dense(inputTensor, outputNodes, 'final_', weight_init=normc_initializer(0.01), bias = useBias)
    return last_out


###### Initializer

ALREADY_INITIALIZED = set()

def initialize():
    """Initialize all the uninitialized variables in the global scope."""
    new_variables = set(tf.global_variables()) - ALREADY_INITIALIZED
    if (new_variables):
        tf.get_default_session().run(tf.variables_initializer(new_variables))
        ALREADY_INITIALIZED.update(new_variables)


###### MLP generators

def continuous_MLP_generator(hiddenNodes):
    def generate(inputTensor, dimOutput):
        return create_layers_linear_ouput(inputTensor, hiddenNodes, dimOutput)
    return generate


def linear_layer_generator(useBias = True):
    def generate(inputTensor, dimOutput):
        return create_linear_layer(inputTensor, dimOutput, useBias)
    return generate

def constant_generator():
    def generate(inputTensor, dimOutput):
        return create_linear_layer(None, dimOutput, True)
    return generate


def diagional_log_std_generator():
    def generate(inputTensor, dimOutput):
        return tf.get_variable("logstd", shape=[dimOutput], initializer=tf.zeros_initializer())
    return generate

def constant_covariance_generator():
    def generate(inputTensor, dimOutput):
        return tf.get_variable("stdmat", shape=[dimOutput, dimOutput], initializer=tf.ones_initializer())
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


def flatgrad(loss, var_list, clip_norm=None):
    grads = tf.gradients(loss, var_list)
    if clip_norm is not None:
        grads = [tf.clip_by_norm(grad, clip_norm=clip_norm) for grad in grads]
    return tf.concat(axis=0, values=[
        tf.reshape(grad if grad is not None else tf.zeros_like(v), [numel(v)])
        for (v, grad) in zip(var_list, grads)
    ])


def singlegrad(loss, var_list):

    y_list = tf.unstack(loss)
    jacobian_list = [tf.gradients(y_, var_list)[0] for y_ in y_list]  # list [grad(y0, x), grad(y1, x), ...]
    jacobian = tf.stack(jacobian_list)
    return jacobian


class GetFlat(object):
    def __init__(self, var_list):
        self.op = tf.concat(axis=0, values=[tf.reshape(v, [numel(v)]) for v in var_list])

    def __call__(self):
        return tf.get_default_session().run(self.op)

def minimize(optimizer, loss, variables):
    operation = optimizer.minimize(loss, variables)
    operation.loss = loss

###### TensorFlow Decorator

def tensor(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate
