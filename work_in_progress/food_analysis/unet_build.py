#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 11:04:11 2017

@author: ajaver
"""
from tensorflow.contrib import keras
Input = keras.layers.Input
Conv2D = keras.layers.Conv2D
MaxPooling2D = keras.layers.MaxPooling2D
Dropout = keras.layers.Dropout
concatenate = keras.layers.concatenate
Conv2DTranspose = keras.layers.Conv2DTranspose
Cropping2D = keras.layers.Cropping2D
Activation = keras.layers.Activation

Model = keras.models.Model

#from keras.models import Model
#from keras.layers import Input, Conv2D, MaxPooling2D, Dropout, \
#concatenate, Conv2DTranspose, Cropping2D, Activation


from math import ceil, floor

def get_unet_model(input_shape = (444, 444, 1), n_outputs=2):
    #    #NOTES:
    #    #Conv2D defaults are:
    #    #kernel_initializer='glorot_uniform' is also known as Xavier
    #    #padding='valid' means "no padding"
    #    
    #    # if we include the batch normalization we could use use_bias=False, 
    #    #x = BatchNormalization(name='norm_d0a-b')(x)
    
    def _get_crop_size(small_m, big_m):
        #Conv2DTranspose so i used the one before (it will become twice as large)
        #for some reason i cannot get the shape after 
        up_conv_s = 2 
        extra_d = [int(b)-up_conv_s*int(s) for s,b in zip(small_m.shape[1:3], big_m.shape[1:3])]
        crop_size = [( int(floor(x/2)), int(ceil(x/2)) ) for x in extra_d]
        return crop_size
    
    data =  Input(shape=input_shape, name='loaddata')
    d0b = Conv2D(64, (3, 3), name='conv_d0a-b', activation='relu')(data)
    d0c = Conv2D(64, (3, 3), name='conv_d0b-c', activation='relu')(d0b)
    
    d1a = MaxPooling2D((2, 2), strides=(2, 2), name='pool_d0c-1a')(d0c)
    d1b = Conv2D(128, (3, 3), name='conv_d1a-b', activation='relu')(d1a)
    d1c = Conv2D(128, (3, 3), name='conv_d1b-c', activation='relu')(d1b)
    
    d2a = MaxPooling2D((2, 2), strides=(2, 2), name='pool_d1c-2a')(d1c)
    d2b = Conv2D(256, (3, 3), name='conv_d2a-b', activation='relu')(d2a)
    d2c = Conv2D(256, (3, 3), name='conv_d2b-c', activation='relu')(d2b)
    
    d3a = MaxPooling2D((2, 2), strides=(2, 2), name='pool_d2c-3a')(d2c)
    d3b = Conv2D(512, (3, 3), name='conv_d3a-b', activation='relu')(d3a)
    d3c = Conv2D(512, (3, 3), name='conv_d3b-c', activation='relu')(d3b)
    d3c = Dropout(0.5, name='dropout_d3c')(d3c)
    
    d4a = MaxPooling2D((2, 2), strides=(2, 2), name='pool_d3c-4a')(d3c)
    d4b = Conv2D(1024, (3, 3), name='conv_d4a-b', activation='relu')(d4a)
    d4c = Conv2D(1024, (3, 3), name='conv_d4b-c', activation='relu')(d4b)
    d4c = Dropout(0.5, name='dropout_d4c')(d4c)
    
    u3a = Conv2DTranspose(512, 
                          (2, 2), 
                          strides=(2, 2),
                          name='upconv_d4c_u3a', 
                          padding='valid',
                          activation='relu')(d4c)
    d3cc = Cropping2D(cropping=_get_crop_size(d4c, d3c), name= 'crop_d3c-d3cc')(d3c)
    u3b = concatenate([u3a, d3cc], axis=3,  name= 'concat_d3cc_u3a-b')
    u3c = Conv2D(512, (3, 3), name='conv_u3b-c', activation='relu')(u3b)
    u3d = Conv2D(512, (3, 3), name='conv_u3c-d', activation='relu')(u3c)
    
    u2a = Conv2DTranspose(256, 
                          (2, 2), 
                          strides=(2, 2),
                          name='upconv_u3d_u2a', 
                          padding='valid',
                          activation='relu')(u3d)
    d2cc = Cropping2D(cropping=_get_crop_size(u3d, d2c), name= 'crop_d2c-d2cc')(d2c)
    u2b = concatenate([u2a, d2cc], axis=3,  name= 'concat_d2cc_u2a-b')
    u2c = Conv2D(256, (3, 3), name='conv_u2b-c', activation='relu')(u2b)
    u2d = Conv2D(256, (3, 3), name='conv_u2c-d', activation='relu')(u2c)
    
    u1a = Conv2DTranspose(128, 
                          (2, 2), 
                          strides=(2, 2),
                          name='upconv_u2d_u1a', 
                          padding='valid',
                          activation='relu')(u2d)
    d1cc = Cropping2D(cropping=_get_crop_size(u2d, d1c), name= 'crop_d1c-d1cc')(d1c)
    u1b = concatenate([u1a, d1cc], axis=3,  name= 'concat_d1cc_u1a-b')
    u1c = Conv2D(128, (3, 3), name='conv_u1b-c', activation='relu')(u1b)
    u1d = Conv2D(128, (3, 3), name='conv_u1c-d', activation='relu')(u1c)
    
    u0a = Conv2DTranspose(64, 
                          (2, 2), 
                          strides=(2, 2),
                          name='upconv_u1d_u0a', 
                          padding='valid',
                          activation='relu')(u1d)
    d0cc = Cropping2D(cropping=_get_crop_size(u1d, d0c), name= 'crop_d0c-d0cc')(d0c)
    u0b = concatenate([u0a, d0cc], axis=3,  name= 'concat_d0cc_u0a-b')
    u0c = Conv2D(64, (3, 3), name='conv_u0b-c', activation='relu')(u0b)
    u0d = Conv2D(64, (3, 3), name='conv_u0c-d', activation='relu')(u0c)
    
    score = Conv2D(n_outputs, (1, 1), name='conv_u0c-score', activation='relu')(u0d)
    loss = Activation('softmax')(score)
    
    model = Model(data, loss)
        
    return model

if __name__ == '__main__':
    mod = get_unet_model((444, 444, 1))