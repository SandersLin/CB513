import lasagne

# 6 conv before FC

#validate_every = 40
start_saving_at = 0
save_every = 20
#write_every_batch = 10

epochs = 300
batch_size = 64
N_CONV_A = 12
N_CONV_B = 12
N_CONV_C = 12
N_CONV_D = 12
N_CONV_E = 12
N_CONV_F = 12
F_CONV_A = 3
F_CONV_B = 5
F_CONV_C = 7
F_CONV_D = 9
F_CONV_E = 13
F_CONV_F = 17
N_L1 = 200
N_LSTM_F = 200
N_LSTM_B = 200
N_L2 = 200
n_inputs = 42
num_classes = 8
seq_len = 700
optimizer = "adagrad"
lambda_reg = 0.0001
cut_grad = 20

learning_rate_schedule = {
    0: 0.025,
    250: 0.005,
    275: 0.0025,
}

def build_model():
    # 1. Input layer
    l_in = lasagne.layers.InputLayer(shape=(None, seq_len, n_inputs))
    l_dim_a = lasagne.layers.DimshuffleLayer(
	l_in, (0,2,1))
    l_conv_a = lasagne.layers.Conv1DLayer(
	incoming=l_dim_a, num_filters=N_CONV_A, pad='same',
	filter_size=F_CONV_A, stride=1, nonlinearity=lasagne.nonlinearities.rectify)
    l_conv_b = lasagne.layers.Conv1DLayer(
	incoming=l_dim_a, num_filters=N_CONV_B, pad='same',
	filter_size=F_CONV_B, stride=1, nonlinearity=lasagne.nonlinearities.rectify)
    l_conv_c = lasagne.layers.Conv1DLayer(
	incoming=l_dim_a, num_filters=N_CONV_C, pad='same',
	filter_size=F_CONV_C, stride=1, nonlinearity=lasagne.nonlinearities.rectify)
    l_conv_d = lasagne.layers.Conv1DLayer(
	incoming=l_dim_a, num_filters=N_CONV_D, pad='same',
	filter_size=F_CONV_D, stride=1, nonlinearity=lasagne.nonlinearities.rectify)
    l_conv_e = lasagne.layers.Conv1DLayer(
	incoming=l_dim_a, num_filters=N_CONV_E, pad='same',
	filter_size=F_CONV_E, stride=1, nonlinearity=lasagne.nonlinearities.rectify)
    l_conv_f = lasagne.layers.Conv1DLayer(
	incoming=l_dim_a, num_filters=N_CONV_F, pad='same',
	filter_size=F_CONV_F, stride=1, nonlinearity=lasagne.nonlinearities.rectify)
    l_c_a = lasagne.layers.ConcatLayer([l_conv_a, l_conv_b, l_conv_c, l_conv_d, l_conv_e, l_conv_f], axis=1)
    l_dim_b = lasagne.layers.DimshuffleLayer(
	l_c_a, (0,2,1))
    l_c_b = lasagne.layers.ConcatLayer([l_in,l_dim_b], axis=2)
    # 2. First Dense Layer    
    l_reshape_a = lasagne.layers.ReshapeLayer(
        l_c_b, (batch_size*seq_len,n_inputs+12*6))
    l_1 = lasagne.layers.DenseLayer(
        l_reshape_a, num_units=N_L1, nonlinearity=lasagne.nonlinearities.rectify)
    l_reshape_b = lasagne.layers.ReshapeLayer(
        l_1, (batch_size, seq_len, N_L1))
#    batch_size, seq_len, _ = l_in.input_var.shape
    # 3. LSTM Layers
#    l_c_b = lasagne.layers.ConcatLayer([l_reshape_b, l_dim_b], axis=2)
    l_forward = lasagne.layers.LSTMLayer(l_reshape_b, N_LSTM_F)
#    l_vertical = lasagne.layers.ConcatLayer([l_in,l_forward], axis=2)
#    l_sum = lasagne.layers.ConcatLayer([l_in, l_forward],axis=-1)
    l_backward = lasagne.layers.LSTMLayer(l_reshape_b, N_LSTM_B, backwards=True)
    
#    out = lasagne.layers.get_output(l_sum, sym_x)
#    out.eval({sym_x: })
    #Concat layer
    l_sum = lasagne.layers.ConcatLayer(incomings=[l_forward, l_backward], axis=2)
    # 4. Second Dense Layer
    l_reshape_b = lasagne.layers.ReshapeLayer(
        l_sum, (batch_size*seq_len, N_LSTM_F+N_LSTM_B))
    # Our output layer is a simple dense connection, with 1 output unit
    l_2 = lasagne.layers.DenseLayer(
	lasagne.layers.dropout(l_reshape_b, p=0.5), num_units=N_L2, nonlinearity=lasagne.nonlinearities.rectify)
    # 5. Output Layer
    l_recurrent_out = lasagne.layers.DenseLayer(
        l_2, num_units=num_classes, nonlinearity=lasagne.nonlinearities.softmax)

    # Now, reshape the output back to the RNN format
    l_out = lasagne.layers.ReshapeLayer(
        l_recurrent_out, (batch_size, seq_len, num_classes))

    return l_in, l_out
