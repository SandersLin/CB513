import lasagne
import numpy as np
import BatchNormLayer
batch_norm = BatchNormLayer.batch_norm

#validate_every = 40
start_saving_at = 0
save_every = 1
#write_every_batch = 10

epochs = 400
batch_size = 64
N_L1 = 200
N_LSTM_F = 400
N_LSTM_B = 400
N_L2 = 200
n_inputs = 42
num_classes = 8
seq_len = 700
optimizer = "rmsprop"
lambda_reg = 0.0001
cut_grad = 20

learning_rate_schedule = {
    0: 0.001,
}

def build_model():
    # 1. Input layer
    l_in = lasagne.layers.InputLayer(shape=(None, seq_len, n_inputs))

    # 2. First Dense Layer
    l_reshape_a = lasagne.layers.ReshapeLayer(
        l_in, (batch_size*seq_len,n_inputs))
    l_1 = lasagne.layers.DenseLayer(
        l_reshape_a, num_units=N_L1, nonlinearity=lasagne.nonlinearities.rectify)

    l_reshape_b = lasagne.layers.ReshapeLayer(
        l_1, (batch_size, seq_len, N_L1))
#    batch_size, seq_len, _ = l_in.input_var.shape
    # 3. LSTM Layers
#    l_c_b = lasagne.layers.ConcatLayer([l_reshape_b, l_dim_b], axis=2)
    l_forward = lasagne.layers.LSTMLayer(l_reshape_b, N_LSTM_F)
    l_vertical = lasagne.layers.ConcatLayer([l_in, l_forward], axis=-1)
    l_backward = lasagne.layers.LSTMLayer(l_vertical, N_LSTM_B, backwards=True)
#    out = lasagne.layers.get_output(l_sum, sym_x)
#    out.eval({sym_x: })
    #Concat layer
    l_concat = lasagne.layers.ConcatLayer(incomings=[l_forward, l_backward], axis=2)
    # 4. Second Dense Layer
    l_reshape_b = lasagne.layers.ReshapeLayer(
        l_concat, (batch_size*seq_len, N_LSTM_F+N_LSTM_B))
    # Our output layer is a simple dense connection, with 1 output unit
    l_2 = lasagne.layers.DenseLayer(
        lasagne.layers.dropout(l_reshape_b, p=0.5), num_units=N_L2,
        nonlinearity=lasagne.nonlinearities.rectify)
#    l_2_b = batch_norm(l_2)
    # 5. Output Layer
    l_recurrent_out = lasagne.layers.DenseLayer(
        l_2, num_units=num_classes, nonlinearity=lasagne.nonlinearities.softmax)

    # Now, reshape the output back to the RNN format
    l_out = lasagne.layers.ReshapeLayer(
        l_recurrent_out, (batch_size, seq_len, num_classes))

    return l_in, l_out
