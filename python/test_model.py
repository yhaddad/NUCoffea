import numpy as np

from tensorflow import keras
from keras import backend as K
from keras.layers import Input,InputLayer, Activation, Dense, Dropout, BatchNormalization, Lambda
from keras.models import Sequential, Model, clone_model
from keras.optimizers import SGD, Adam, Adadelta, Adagrad

def absolute_BinaryCrossentropy (y_true, y_pred, weights): 
    error = K.abs(K.sum(weights*(K.maximum(y_pred,0) - y_pred*y_true + K.log(1+K.exp(-1*K.abs(y_pred)))),axis=-1))
    return error

def custom_relu(X):
    return K.maximum(K.minimum(X,100-3*X),0)

def get_models():
    NINPUT_3J = 27
    NINPUT_2J = 22

    print('====================')
    print('loading models...')
    print('====================')

    nn_input_3J = Input((NINPUT_3J,))
    y_true_3J = Input((1,),name='y_true_3J')
    weights_3J = Input((1,), name='weights_3J')

    nn_input_2 = Input((NINPUT_2J,))
    y_true_2 = Input((1,),name='y_true_2')
    weights_2 = Input((1,), name='weights_2')

    h_3J = BatchNormalization()(nn_input_3J)
    X_3J = Dense((200), name='hidden_1')(h_3J)
    h_3J = Lambda(custom_relu, name='custom_relu')(X_3J)
    (out_z_3J)=Dense((1), name='out_z_3J')(h_3J)
    out_3J = Activation('sigmoid',name='out_3J')(out_z_3J)

    h_2J = BatchNormalization()(nn_input_2)
    X_2J = Dense((100), name='hidden_12')(h_2J)
    h_2J = Lambda(custom_relu, name='custom_relu2')(X_2J)
    (out_z_2J) = Dense((1), name='out_z_2J')(h_2J)
    out_2J = Activation('sigmoid',name='out_2J')(out_z_2J)

    model_3J = Model(inputs=[nn_input_3J, weights_3J, y_true_3J], outputs=out_3J)
    model_2J = Model(inputs=[nn_input_2, weights_2, y_true_2], outputs=out_2J)

    model_3J.add_loss(absolute_BinaryCrossentropy(y_true_3J, out_z_3J, weights_3J))
    model_2J.add_loss(absolute_BinaryCrossentropy(y_true_2, out_z_2J, weights_2))

    optim_3J = Adam(lr = 0.001)
    optim_2J = Adam(lr = 0.001)

    model_3J.compile(optimizer=optim_3J, loss=None, weighted_metrics=['accuracy'])
    model_2J.compile(optimizer=optim_2J, loss=None, weighted_metrics=['accuracy'])

    return model_3J, model_2J


def get_inputs():
    lep_category = 123
    ngood_bjets = 123
    lead_jet_pt = 123
    trail_jet_pt = 123
    leading_lep_pt = 123
    trailing_lep_pt = 123
    lead_jet_eta = 123
    trail_jet_eta = 123
    leading_lep_eta = 123
    trailing_lep_eta = 123
    lead_jet_phi = 123
    trail_jet_phi = 123
    leading_lep_phi = 123
    trailing_lep_phi = 123
    met_pt = 123
    met_phi = 123
    delta_phi_j_met = 123
    delta_phi_ZMet = 123
    Z_mass = 123
    dijet_Mjj = 123
    dijet_abs_dEta = 123
    year = 123

    NN_input = [lep_category, ngood_bjets, lead_jet_pt, trail_jet_pt, leading_lep_pt, trailing_lep_pt, lead_jet_eta, trail_jet_eta, leading_lep_eta, trailing_lep_eta, lead_jet_phi, trail_jet_phi, leading_lep_phi, trailing_lep_phi, met_pt, met_phi, delta_phi_j_met, delta_phi_ZMet, Z_mass, dijet_Mjj, dijet_abs_dEta, year, -1, -1]
    NN_input = np.array([NN_input,])

    return NN_input

def main():
    # construct models
    model_3J, model_2J = get_models()
    # load model weights
    model_2J.load_weights('exactly2Jets_weights.h5')
    # example input
    NN_input = get_inputs()
    # prediction
    NN_score = model_2J.predict([NN_input[:,0:22],NN_input[:,22],NN_input[:,23]])
    NN_score = NN_score.item()
    print('NN_score:', NN_score)

    return

if __name__ == '__main__':
    main()
