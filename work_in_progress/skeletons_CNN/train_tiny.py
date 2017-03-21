#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 17:39:21 2017

@author: ajaver
"""
import tables
import numpy as np
import matplotlib.pylab as plt
import time
import os

from keras.models import Sequential
from keras.models import Model

from keras import layers
from keras.layers import Conv2D
from keras.layers import BatchNormalization
from keras.layers import Activation
from keras.layers import Input
from keras.layers import MaxPooling2D
from keras.layers import GlobalMaxPooling2D
from keras.layers import GlobalAveragePooling2D
from keras.layers import Dense
from keras.layers import Reshape
from keras.layers import Flatten
from keras.layers import Dropout

from keras.models import load_model
from keras.callbacks import TensorBoard, ModelCheckpoint, History
from keras.optimizers import Adam


def test_res():
    input_shape = (roi_size, roi_size, 1)
    img_input =  Input(shape=input_shape)
    x = Conv2D(32, (3, 3), use_bias=False, name='block1_conv1')(img_input) #strides=(2, 2),
    x = BatchNormalization(name='block1_conv1_bn')(x)
    x = Activation('relu', name='block1_conv1_act')(x)
    x = Conv2D(64, (3, 3), use_bias=False, name='block1_conv2')(x)
    x = BatchNormalization(name='block1_conv2_bn')(x)
    x = Activation('relu', name='block1_conv2_act')(x)
    
    
    residual = Conv2D(128, (1, 1), strides=(2, 2), padding='same', use_bias=False)(x)
    residual = BatchNormalization()(residual)
    
    x = Conv2D(128, (3, 3), padding='same', use_bias=False, name='block2_conv1')(x)
    x = BatchNormalization(name='block2_conv1_bn')(x)
    x = Activation('relu', name='block2_conv2_act')(x)
    x = Conv2D(128, (3, 3), padding='same', use_bias=False, name='block2_conv2')(x)
    x = BatchNormalization(name='block2_conv2_bn')(x)
    
    x = MaxPooling2D((3, 3), strides=(2, 2), padding='same', name='block2_pool')(x)
    x = layers.add([x, residual])
    
    
    residual = Conv2D(256, (1, 1), strides=(2, 2), padding='same', use_bias=False)(x)
    residual = BatchNormalization()(residual)
    
    
    x = Activation('relu', name='block3_conv1_act')(x)
    x = Conv2D(256, (3, 3), padding='same', use_bias=False, name='block3_conv1')(x)
    x = BatchNormalization(name='block3_conv1_bn')(x)
    x = Activation('relu', name='block3_conv2_act')(x)
    x = Conv2D(256, (3, 3), padding='same', use_bias=False, name='block3_conv2')(x)
    x = BatchNormalization(name='block3_conv2_bn')(x)
    
    x = MaxPooling2D((3, 3), strides=(2, 2), padding='same', name='block3_pool')(x)
    x = layers.add([x, residual])
    
    x = GlobalAveragePooling2D(name='avg_pool')(x)
    x = Dense(out_size[0]*out_size[1], activation='relu', name='skeleton')(x)
    x = Reshape((out_size))(x)
    
    model = Model(img_input, x, name='test4_xception')
    model.compile(loss='mean_squared_error',
                  optimizer=Adam(lr=1e-3, decay=0.05),
                  metrics=['mean_absolute_percentage_error'])


def test_large():
    #does not converge
    x = Conv2D(16, (3, 3), use_bias=False, name='conv0')(img_input)
    x = BatchNormalization(name='conv0_bn')(x)
    x = Activation('relu', name='conv0_act')(x)
    x = MaxPooling2D((2, 2), padding='same', name='conv0_pool')(x)
    
    x = Conv2D(32, (3, 3), use_bias=False, name='conv1_1')(img_input)
    x = BatchNormalization(name='conv1_bn1')(x)
    x = Activation('relu', name='conv1_act1')(x)
    
    x = Conv2D(32, (3, 3), use_bias=False, name='conv1_2')(img_input)
    x = BatchNormalization(name='conv1_bn2')(x)
    x = Activation('relu', name='conv1_act2')(x)
    x = MaxPooling2D((2, 2), padding='same', name='conv1_pool')(x)
    
    x = Conv2D(64, (3, 3), use_bias=False, name='conv2_1')(x)
    x = BatchNormalization(name='conv2_bn1')(x)
    x = Activation('relu', name='conv2_act1')(x)
    
    x = Conv2D(64, (3, 3), use_bias=False, name='conv2_2')(x)
    x = BatchNormalization(name='conv2_bn2')(x)
    x = Activation('relu', name='conv2_act2')(x)
    x = MaxPooling2D((2, 2), padding='same', name='conv2_pool')(x)
    
    x = Conv2D(128, (3, 3), use_bias=False, name='conv3_1')(x)
    x = BatchNormalization(name='conv3_bn1')(x)
    x = Activation('relu', name='conv3_act1')(x)
    
    x = Conv2D(128, (3, 3), use_bias=False, name='conv3_2')(x)
    x = BatchNormalization(name='conv3_bn2')(x)
    x = Activation('relu', name='conv3_act2')(x)
    x = MaxPooling2D((2, 2), padding='same', name='conv3_pool')(x)
    
    x = Flatten()(x)
    x = Dense(4092, activation='relu', name='dense')(x)
    x = Dense(out_size[0]*out_size[1], activation='tanh', name='skeleton')(x)
    x = Reshape((out_size))(x)

def test4():
    #does not converge
    x = Conv2D(32, (3, 3), name='conv0_1')(img_input)
    x = BatchNormalization(name='conv0_bn1')(x)
    x = Activation('relu', name='conv0_act1')(x)
    
    #x = Conv2D(32, (3, 3), name='conv0_2')(img_input)
    #x = BatchNormalization(name='conv0_bn2')(x)
    #x = Activation('relu', name='conv0_act2')(x)
    
    x = MaxPooling2D((2, 2), name='conv0_pool')(x)
    
    x = Conv2D(64, (3, 3), name='conv1_1')(x)
    x = BatchNormalization(name='conv1_bn1')(x)
    x = Activation('relu', name='conv1_act1')(x)
    x = MaxPooling2D((2, 2), name='conv1_pool')(x)
    
    x = Conv2D(128, (3, 3), name='conv2_1')(x)
    x = BatchNormalization(name='conv2_bn1')(x)
    x = Activation('relu', name='conv2_act1')(x)
    
    x = Flatten()(x)
    x = Dense(4096, activation='relu', name='dense1')(x)
    x = Dropout(0.5)(x)
    
    x = Dense(1024, activation='relu', name='dense2')(x)
    x = Dropout(0.2)(x)
    
    x = Dense(256, activation='relu', name='dense3')(x)
    x = Dropout(0.2)(x)
    
    x = Dense(out_size[0]*out_size[1], activation='relu', name='skeleton')(x)
    x = Reshape((out_size))(x)


def test5():
    #converges based in the best results i have gotten so far
#    x = Conv2D(64, (3, 3), name='conv0')(img_input)
#    x = Activation('relu', name='conv0_act')(x)
#    
#    x = Conv2D(64, (3, 3), name='conv1')(img_input)
#    x = Activation('relu', name='conv1_act')(x)
#    x = MaxPooling2D((2, 2), name='conv1_pool')(x)
#    
    x = Conv2D(64, (3, 3), name='conv2')(img_input)
    x = Activation('relu', name='conv2_act')(x)
    x = MaxPooling2D((2, 2), name='conv2_pool')(x)
    
    x = Flatten()(x)
    
    x = Dense(1024, name='dense1', activation='relu')(x)
    x = Dropout(0.5)(x)
    
    x = Dense(512, name='dense2', activation='relu')(x)
    x = Dropout(0.4)(x)
    
    x = Dense(256, name='dense3', activation='relu')(x)
    x = Dropout(0.2)(x)
    
    x = Dense(out_size[0]*out_size[1], activation='relu', name='skeleton')(x)
    x = Reshape((out_size))(x)

def test6():
    #very slow, maybe stuck at 20
    input_shape = (roi_size, roi_size, 1)
    img_input =  Input(shape=input_shape)
    
    x = Conv2D(64, (3, 3), name='conv0')(img_input)
    x = Activation('relu', name='conv0_act')(x)
    x = MaxPooling2D((2, 2), name='conv0_pool')(x)
    
    x = Conv2D(128, (3, 3), name='conv1')(x)
    x = BatchNormalization(name='conv1_bn')(x)
    x = Activation('relu', name='conv1_act')(x)
    x = MaxPooling2D((2, 2), name='conv1_pool')(x)
    
    x = Conv2D(256, (3, 3), name='conv2')(x)
    x = BatchNormalization(name='conv2_bn')(x)
    x = Activation('relu', name='conv2_act')(x)
    x = MaxPooling2D((2, 2), name='conv2_pool')(x)
    
    
    x = Flatten()(x)
    
    x = Dense(1024, name='dense1', activation='relu')(x)
    x = Dropout(0.5)(x)
    
    x = Dense(512, name='dense2', activation='relu')(x)
    x = Dropout(0.4)(x)
    
    x = Dense(256, name='dense3', activation='relu')(x)
    x = Dropout(0.2)(x)
    
    x = Dense(out_size[0]*out_size[1], activation='relu', name='skeleton')(x)
    x = Reshape((out_size))(x)

def test7():
    #does not converge
    
    
    x = Conv2D(64, (3, 3), name='conv0')(img_input)
    x = Activation('relu', name='conv0_act')(x)
    x = MaxPooling2D((2, 2), name='conv0_pool')(x)
    
    x = Conv2D(128, (3, 3), name='conv1')(x)
    x = BatchNormalization(name='conv1_bn')(x)
    x = Activation('relu', name='conv1_act')(x)
    x = MaxPooling2D((2, 2), name='conv1_pool')(x)
    
    x = Conv2D(256, (3, 3), name='conv2')(x)
    x = BatchNormalization(name='conv2_bn')(x)
    x = Activation('relu', name='conv2_act')(x)
    x = MaxPooling2D((2, 2), name='conv2_pool')(x)
    
    x = Conv2D(512, (3, 3), name='conv3')(x)
    x = BatchNormalization(name='conv3_bn')(x)
    x = Activation('relu', name='conv3_act')(x)
    x = MaxPooling2D((2, 2), name='conv3_pool')(x)
    
    x = Conv2D(1024, (3, 3), name='conv4')(x)
    x = BatchNormalization(name='conv4_bn')(x)
    x = Activation('relu', name='conv4_act')(x)
    
    x = Flatten()(x)
    #x = GlobalAveragePooling2D(name='avg_pool')(x)
    
    x = Dense(1024, name='dense1', activation='tanh')(x)
    x = Dropout(0.5)(x)
    
    x = Dense(512, name='dense2', activation='tanh')(x)
    x = Dropout(0.4)(x)
    
    x = Dense(256, name='dense3', activation='tanh')(x)
    x = Dropout(0.2)(x)
    
    x = Dense(out_size[0]*out_size[1], activation='tanh', name='skeleton')(x)
    x = Reshape((out_size))(x)
    
    
    model = Model(img_input, x, name='test4_xception')
    model.compile(loss='mean_absolute_error',
                  optimizer=Adam(lr=1e-3),#, decay=0.05),
                  metrics=['mean_absolute_error', 'mean_squared_error', 'mean_absolute_percentage_error'])

def test8():
#kinda works, but the output get stucks in the lower, cannot make it convert properly
#i suspect it is related with the padding
    x = Conv2D(32, (3, 3), padding='same', name='conv0')(img_input)
    x = Activation('elu', name='conv0_act')(x)
    x = MaxPooling2D((2, 2), name='conv0_pool')(x)
    
    x = Conv2D(64, (3, 3), padding='same', name='conv1a')(x)
    x = BatchNormalization(name='conv1a_bn')(x)
    x = Activation('elu', name='conv1a_act')(x)
    
    x = Conv2D(64, (3, 3), padding='same', name='conv1b')(x)
    x = BatchNormalization(name='conv1b_bn')(x)
    x = Activation('elu', name='conv1b_act')(x)
    x = MaxPooling2D((2, 2), name='conv1_pool')(x)
    
    x = Conv2D(128, (3, 3), padding='same', name='conv2a')(x)
    x = BatchNormalization(name='conv2a_bn')(x)
    x = Activation('elu', name='conv2a_act')(x)
    
    x = Conv2D(128, (3, 3), padding='same', name='conv2b')(x)
    x = Activation('elu', name='conv2b_act')(x)
    x = GlobalMaxPooling2D(name='avg_pool')(x)
    
    x = Dense(128, name='dense1', activation='elu')(x)
    x = Dropout(0.2)(x)
    
    x = Dense(128, name='dense2', activation='elu')(x)
    x = Dropout(0.2)(x)
    
    x = Dense(out_size[0]*out_size[1], activation='elu', name='skeleton')(x)
    x = Reshape((out_size))(x)


def test9():
    x = Conv2D(32, (3, 3), padding='same', name='conv0')(img_input)
    x = Activation('elu', name='conv0_act')(x)
    x = MaxPooling2D((2, 2), name='conv0_pool')(x)
    
    x = Conv2D(64, (3, 3), padding='same', name='conv1a')(x)
    x = BatchNormalization(name='conv1a_bn')(x)
    x = Activation('elu', name='conv1a_act')(x)
    
    x = Conv2D(64, (3, 3), padding='same', name='conv1b')(x)
    x = BatchNormalization(name='conv1b_bn')(x)
    x = Activation('elu', name='conv1b_act')(x)
    
    x = MaxPooling2D((2, 2), name='conv1_pool')(x)
    
    x = Conv2D(128, (3, 3), padding='same', name='conv2a')(x)
    x = BatchNormalization(name='conv2a_bn')(x)
    x = Activation('elu', name='conv2a_act')(x)
    
    x = Conv2D(128, (3, 3), padding='same', name='conv2b')(x)
    x = BatchNormalization(name='conv2b_bn')(x)
    x = Activation('elu', name='conv2b_act')(x)
    
    
    #x = GlobalMaxPooling2D(name='avg_pool')(x)
    
    x = Flatten()(x)
    x = Dense(2048, name='dense0', activation='elu')(x)
    x = Dropout(0.4)(x)
    
    x = Dense(1024, name='dense1', activation='elu')(x)
    x = Dropout(0.4)(x)
    
    x = Dense(128, name='dense2', activation='elu')(x)
    x = Dropout(0.2)(x)
    
    x = Dense(out_size[0]*out_size[1], activation='elu', name='skeleton')(x)
    x = Reshape((out_size))(x)

    model = Model(img_input, x)
    optimizer = Adam(lr=1e-3)#, decay=0.05)
    model.compile(loss='mean_absolute_error',
                  optimizer=optimizer,
                  metrics=['mean_absolute_error', 'mean_squared_error', 'mean_absolute_percentage_error'])
    

# for reproducibility
rand_seed = 1337
np.random.seed(rand_seed)  

out_size = (49, 2)
roi_size = 128


# convolution kernel size
kernel_size = (3, 3)
    

input_shape = (roi_size, roi_size, 1)
img_input =  Input(shape=input_shape)

x = Conv2D(32, (3, 3), padding='same', name='conv0')(img_input)
x = Activation('elu', name='conv0_act')(x)
x = MaxPooling2D((2, 2), name='conv0_pool')(x)

x = Conv2D(64, (3, 3), padding='same', name='conv1a')(x)
x = BatchNormalization(name='conv1a_bn')(x)
x = Activation('elu', name='conv1a_act')(x)

x = Conv2D(64, (3, 3), padding='same', name='conv1b')(x)
x = BatchNormalization(name='conv1b_bn')(x)
x = Activation('elu', name='conv1b_act')(x)

x = MaxPooling2D((2, 2), name='conv1_pool')(x)

x = Conv2D(128, (3, 3), padding='same', name='conv2a')(x)
x = BatchNormalization(name='conv2a_bn')(x)
x = Activation('elu', name='conv2a_act')(x)

x = Conv2D(128, (3, 3), padding='same', name='conv2b')(x)
x = BatchNormalization(name='conv2b_bn')(x)
x = Activation('elu', name='conv2b_act')(x)


x = MaxPooling2D((2, 2), name='conv2_pool')(x)

x = Conv2D(256, (3, 3), padding='same', name='conv3a')(x)
x = BatchNormalization(name='conv3a_bn')(x)
x = Activation('elu', name='conv3a_act')(x)

x = Conv2D(256, (3, 3), padding='same', name='conv3b')(x)
x = BatchNormalization(name='conv3b_bn')(x)
x = Activation('elu', name='conv3b_act')(x)


x = GlobalMaxPooling2D(name='avg_pool')(x)

#x = Flatten()(x)
x = Dense(1024, name='dense0', activation='elu')(x)
x = Dropout(0.4)(x)

x = Dense(512, name='dense1', activation='elu')(x)
x = Dropout(0.4)(x)

x = Dense(128, name='dense2', activation='elu')(x)
x = Dropout(0.2)(x)

x = Dense(out_size[0]*out_size[1], activation='elu', name='skeleton')(x)
x = Reshape((out_size))(x)



model = Model(img_input, x)
optimizer = Adam(lr=1e-3)#, decay=0.05)
model.compile(loss='mean_absolute_error',
              optimizer=optimizer,
              metrics=['mean_absolute_error', 'mean_squared_error', 'mean_absolute_percentage_error'])

#%%
def _get_index(events_tot, val_frac, test_frac):
    inds = np.random.permutation(events_tot)
    test_size = np.round(events_tot*test_frac).astype(np.int)
    val_size = np.round(events_tot*val_frac).astype(np.int)
    
    
    all_ind = {'test' : inds[:test_size], 
               'val': inds[test_size:(val_size+test_size)],
               'train' : inds[(val_size+test_size):]}
    
    return all_ind

#%%

sample_file = 'N2 on food R_2011_03_09__11_58_06___6___3_sample.hdf5'
with tables.File(sample_file, 'r') as fid:
    #select a tiny sample
    tot = fid.get_node('/mask').shape[0]
    inds = np.random.permutation(tot)[:128]
    X = fid.get_node('/mask')[inds, :, :][:, :, :, np.newaxis]
    Y = fid.get_node('/skeleton')[inds, :, :]
    roi_size = X.shape[1]
    
    #Y = Y/roi_size
    
    Y = (Y-(roi_size/2.))/roi_size*2
    #X = -(X-np.mean(X, axis=(1,2)))
    
#%%


log_dir = './tiny_logs_%s' % time.strftime('%Y%m%d_%H%M%S')
checkpoint_file = os.path.join(log_dir, 'tiny-{epoch:02d}-{loss:.2f}.h5')
history = History()

tb = TensorBoard(log_dir=log_dir, histogram_freq=1, write_graph=True, write_images=True)
mcp = ModelCheckpoint(checkpoint_file, verbose=0,  mode='auto', period=50)

epochs = 2000
model.fit(X,Y, batch_size=128, 
          epochs=epochs, 
          verbose=1, callbacks=[tb, mcp, history])

    
    #%%




#for i in range(10):
#    
#    model.fit(X,Y, batch_size=128, 
#              epochs=epochs, 
#              verbose=1)#, callbacks=[tb])
#    
#    
#    Y_pred = model.predict(X)
#    roi_size = X.shape[1]
#    #Y_pred = Y_pred*roi_size
#    #Y_c = Y*roi_size + roi_size/2.
#    #Y_c = Y*roi_size
#    #
#    
#    ind = 0
#    plt.figure()
#    #plt.imshow(np.squeeze(X[ind]), interpolation='None', cmap='gray')
#    #plt.grid('off')
#    Y_c = Y
#    plt.plot(Y_c[ind, :, 0], Y_c[ind, :, 1], '.r')
#    plt.plot(Y_c[ind, 0, 0], Y_c[ind, 0, 1], 'sr')
#    plt.plot(Y_pred[ind, :, 0], Y_pred[ind, :, 1], '.-b')
#    plt.plot(Y_pred[ind, 0, 0], Y_pred[ind, 0, 1], 'ob')
#    #model.save('skels_tiny_{}.h5'.format((i+1)*nb_epoch))
#%%
##%%
##nb_epoch = 10
##for i in range(20):
##    model.fit(X_train, Y_train, batch_size=128, nb_epoch=nb_epoch,
##                  verbose=1, validation_data=(X_val, Y_val))
##    model.save('skels_mod_{}.h5'.format((i+1)*nb_epoch))
#
##%%
#
#X, Y = X_train, Y_train

#model = load_model('skels_mod_40.h5')






