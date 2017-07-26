#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 11 18:58:42 2017

@author: ajaver
"""

import tables
import numpy as np
import pandas as pd
from math import ceil
import random
import matplotlib.pylab as plt
from skimage.transform import resize
from skimage.morphology import binary_erosion

from keras.preprocessing.image import Iterator
from keras.utils import to_categorical

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'find_food'))

from augmentation import random_transform, transform_img

def process_seq(seq_x, seq_y, coords, im_size=(128,128), y_weight=1):
    seq_x = np.rollaxis(seq_x, 0, 3)
    seq_x = seq_x.astype(np.float32)
    
    seq_y = to_categorical(seq_y,2)
    seq_y[:,1] = seq_y[:,1]*y_weight
        
    seq_x_crop = crop_seq(seq_x, coords)
    seq_x_crop = normalize_seq(seq_x_crop)
    seq_x_crop = resize(seq_x_crop, im_size, mode='reflect')
    
    return seq_x_crop, seq_y

def crop_seq(seq_x, coords, rand_d_roi=0, rand_shift_x=0, rand_shift_y=0):
    def _correct_range(ini, fin, n_size):
        less_n = ini<0
        if np.any(less_n):
            fin[less_n] -= ini[less_n]
            ini[less_n] = 0
        
        more_n = fin > n_size
        if np.any(more_n):
            ini[more_n] += n_size - fin[more_n]
            fin[more_n] = n_size
        return ini, fin
    
    r_size = coords['roi_size'].values.astype(np.int)
    assert np.all(r_size==r_size[0])
    r_size = r_size[0] + rand_d_roi
    
    r_size = min(r_size, min(seq_x.shape[0:2]))
    
    
    j_ini = np.ceil(coords['coord_x'] - r_size/2).values.astype(np.int)
    i_ini = np.ceil(coords['coord_y'] - r_size/2).values.astype(np.int)
    
    j_ini += rand_shift_x
    i_ini += rand_shift_y
    
    
    j_fin = j_ini + r_size
    i_fin = i_ini + r_size
    
    
    i_ini, i_fin = _correct_range(i_ini, i_fin, seq_x.shape[0])
    j_ini, j_fin = _correct_range(j_ini, j_fin, seq_x.shape[1])
    
    seq_x_r = np.zeros((r_size, r_size, seq_x.shape[-1]))
    for ns, (i_0,i_f, j_0, j_f) in enumerate(zip(i_ini, i_fin,j_ini, j_fin)):
        seq_x_r[..., ns] = seq_x[i_0:i_f, j_0:j_f, ns]
    #%%        
    return seq_x_r

def plot_seq(seq):   
    nseq = seq.shape[-1]
    ncols = 4
    nrows = int(ceil(nseq/ncols))
    plt.figure(figsize=(2*ncols, 2*nrows))
    for ii in range(nseq):
        ind = ii +1 if ii <7 else ii +2
        ax = plt.subplot(nrows, ncols, ind)
        
        plt.imshow(seq[..., ii], cmap='gray', interpolation='none')
        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
#%%
def normalize_seq(seq, channel_axis=-1):
    
    assert channel_axis == -1 or channel_axis == 0
    seq_e = seq>0
    
    if channel_axis == -1:
        for nn in range(seq.shape[-1]):
            seq_e[..., nn] -= binary_erosion(seq_e[..., nn])
    else:
        for nn in range(seq.shape[0]):
            seq_e[nn] -= binary_erosion(seq_e[nn])
    
    seq[seq>0] -= np.median(seq[seq_e])
    seq /= 255.
    
    return seq
#%%
class DirectoryImgGenerator(object):
    def __init__(self, 
                 file_name,
                 im_size, 
                 y_weight = 20, 
                 is_train = True,
                 is_tiny = False
                 ):
        
        
        self.file_name = file_name
        self.y_weight = y_weight
        self.im_size = im_size
        
        with pd.HDFStore(self.file_name, "r") as fid:
            coordinates_data = fid['/coordinates_data']
        
        set_type = 'train'if is_train else 'val'
        group_type = 'tiny' if is_tiny else 'partitions'
        
        
        with tables.File(self.file_name, "r") as fid:
            self.n_seq = fid.get_node('/X').shape[1]
            hpath = '/{}/{}'.format(group_type, set_type)
            self.valid_indexes = fid.get_node(hpath)[:]
            
        valid = coordinates_data['seq_index'].isin(self.valid_indexes)
        coordinates_data = coordinates_data[valid]
            
        self.coordinates_data_g = coordinates_data.groupby('seq_index')
        self.valid_rows = list(self.coordinates_data_g.groups.keys())
        self.tot = len(self.valid_rows)
        
    def __len__(self): 
        return self.tot

    def __getitem__(self, i):
        return self._get(i)

    def __iter__(self):
        for nn in self.valid_rows:
            yield self._get(nn)
    
    def get_random(self):
        ii = random.choice(self.valid_rows)
        return self._get(ii)
    
    def _get(self, nn):
        
        coords = self.coordinates_data_g.get_group(nn)
        coords = coords.sort_values('frame_number')
        with tables.File(self.file_name, "r") as fid:
            seq_x = fid.get_node('/X')[nn]
            seq_y = fid.get_node('/Y')[nn]
        
        seq_x, seq_y = process_seq(seq_x, 
                                   seq_y, 
                                   coords, 
                                   im_size=self.im_size, 
                                   y_weight = self.y_weight
                                   )
        return seq_x, seq_y

def process_data(seq_x, 
                 seq_y, 
                 window_size = 4, 
                 y_offset_left = 0,
                 y_offset_right = 0,
                 transform_ags = {}
                 ):
    
    assert window_size-y_offset_right > y_offset_left
    
    if len(transform_ags) > 0:
        if 'int_alpha' in transform_ags:
            transform_ags = transform_ags.copy()
            int_alpha = transform_ags['int_alpha']
            del transform_ags['int_alpha']
            
        h,w = seq_x.shape[:-1]
        transform = random_transform(h,w, **transform_ags)
        seq_x = transform_img(seq_x, *transform)
    
        if int_alpha is not None:
            alpha = np.random.uniform(int_alpha[0], int_alpha[1])
            seq_x *= alpha
        
    
    #divide in smaller sequence in random order
    n_seq = seq_x.shape[-1]
    inds = range(n_seq - window_size)
    
    seq_x_d = [seq_x[:,:,i:i+window_size] for i in inds]
    seq_y_d = [seq_y[i+y_offset_left:i+window_size-y_offset_right] for i in inds]
    
    return seq_x_d, seq_y_d
    


class ImageMaskGenerator(Iterator):
    def __init__(self, 
                 generator,
                 transform_ags,
                 window_size = 4,
                 y_offset_left = 0,
                 y_offset_right = 0,
                 batch_size=32, 
                 shuffle=True, 
                 seed=None
                 ):
        
        
       
        self.generator = generator
        
        #total number of samples
        tot = len(self.generator)*(self.generator.n_seq - window_size)//batch_size
        self.tot_samples = tot
        
        self.transform_ags = transform_ags
        self.batch_size = batch_size
        self.window_size = window_size
        self.y_offset_left = y_offset_left
        self.y_offset_right = y_offset_right
        assert window_size-y_offset_right > y_offset_left
        
        
        #i really do not use this functionality i could reimplement it in the future
        super(ImageMaskGenerator, self).__init__(self.tot_samples, batch_size, shuffle, seed)

    def next(self):
        """
        # Returns
            The next batch.
        """
        
        n_seq_t = self.generator.n_seq - self.window_size
        seq_x_t = []
        seq_y_t = []
        
        for ii in range(int(ceil(self.batch_size/n_seq_t))):
            seq_x, seq_y = self.generator.get_random()
            xx, yy = process_data(seq_x, 
                                  seq_y, 
                                  window_size=self.window_size, 
                                  y_offset_left=self.y_offset_left, 
                                  y_offset_right=self.y_offset_right, 
                                  transform_ags=self.transform_ags
                                  )
            seq_x_t += xx
            seq_y_t += yy
        
        #sample and only select batch_size samples
        D = list(zip(seq_x_t, seq_y_t))
        D = random.sample(D, self.batch_size)
        seq_x_t, seq_y_t = map(np.stack, zip(*D))
        
        
        return seq_x_t, seq_y_t

#%%
if __name__ == '__main__':
    import os
    save_dir = '/Users/ajaver/OneDrive - Imperial College London/egg_laying'
    save_name = os.path.join(save_dir, 'train_data_eggs.hdf5')
    im_size = (128, 128)
    transform_ags = dict(
             rotation_range=90, 
             shift_range = 0.1,
             zoom_range = (0.75, 1.5),
             same_zoom = True,
             horizontal_flip = True,
             vertical_flip = True,
             elastic_alpha_range = 400,
             elastic_sigma=15,
             int_alpha = (0.5,2.25)
             )
    
    window_size = 7
    y_offset_left = 2
    y_offset_right = 2
    batch_size = 5
    
    gen_d = DirectoryImgGenerator(save_name, 
                                  im_size, 
                                  is_train = False,
                                  is_tiny = True
                                  )
    
    gen = ImageMaskGenerator(gen_d,
                             transform_ags=transform_ags,
                             window_size=window_size,
                             y_offset_left = y_offset_left,
                             y_offset_right = y_offset_right,
                             batch_size = batch_size
                             )
    
#    import time
#    tic = time.time()
#    for nn, (batch_x, batch_y) in enumerate(gen_d):
#        print(nn, time.time() - tic)
#        tic = time.time()
    
    batch_x, batch_y = next(gen)
    
    #%% plot batch
    for nn in range(batch_x.shape[0]):
        seq_x = batch_x[nn]
        seq_y = batch_y[nn]
        ncols = seq_x.shape[-1]
        
        plt.figure()
        for ii in range(ncols):
            plt.subplot(1, ncols, ii+1)
            plt.imshow(seq_x[...,ii])
            
            yi = ii-y_offset_left
            if yi >= 0 and yi < seq_y.shape[0]:
                plt.title(seq_y[ii-y_offset_left])
        
    
    