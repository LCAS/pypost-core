
import tensorflow as tf
import numpy as np

W = tf.get_variable("w", [10,1])
b = tf.get_variable("b", [2])

X = tf.placeholder(dtype=tf.float32, shape=(100,10))
Y = tf.placeholder(dtype=tf.float32, shape=(100,2))

X_data = np.random.normal(0, 1, (100,10))

W_data = np.random.normal(0, 1, (10,2))
Y_data = X_data.dot(W_data)

Y_pred = tf.matmul(X,W) + b
squarredError = tf.reduce_sum(tf.reduce_sum(tf.square(Y_pred - Y), axis = 0),axis=0)

optimizer = tf.train.GradientDescentOptimizer(0.00005)
train = optimizer.minimize(squarredError, var_list=[W, b])

init = tf.initialize_all_variables()


def optimize():
    with tf.Session() as session:
        session.run(init)
        print("starting at", "W:", session.run(W), "b:", session.run(b), "Error:", session.run(squarredError, feed_dict={X : X_data, Y : Y_data}))
        for step in range(10):
            session.run(train, feed_dict={X : X_data, Y : Y_data})
            print("step", step, "W:", session.run(W), "b:", session.run(b), "Error:", session.run(squarredError, feed_dict={X : X_data, Y : Y_data}))


optimize()