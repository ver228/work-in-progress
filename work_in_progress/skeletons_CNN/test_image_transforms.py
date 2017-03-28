#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 10:47:34 2017

@author: ajaver
"""
import numpy as np
import tables
import scipy.ndimage as ndi

def random_rotation(x, y, rg, row_axis=1, col_axis=2, channel_axis=0,
                    fill_mode='nearest', cval=0.):
    """Performs a random rotation of a Numpy image tensor.
    # Arguments
        x: Input tensor. Must be 3D.
        rg: Rotation range, in degrees.
        row_axis: Index of axis for rows in the input tensor.
        col_axis: Index of axis for columns in the input tensor.
        channel_axis: Index of axis for channels in the input tensor.
        fill_mode: Points outside the boundaries of the input
            are filled according to the given mode
            (one of `{'constant', 'nearest', 'reflect', 'wrap'}`).
        cval: Value used for points outside the boundaries
            of the input if `mode='constant'`.
    # Returns
        Rotated Numpy image tensor.
    """
    theta = np.pi / 180 * np.random.uniform(-rg, rg)
    rotation_matrix = np.array([[np.cos(theta), -np.sin(theta), 0],
                                [np.sin(theta), np.cos(theta), 0],
                                [0, 0, 1]])

    h, w = x.shape[row_axis], x.shape[col_axis]
    transform_matrix = transform_matrix_offset_center(rotation_matrix, h, w)
    x = apply_transform_img(x, transform_matrix, channel_axis, fill_mode, cval)
    
    y = apply_transform_coord(y, transform_matrix)
    
    return x, y

def random_shift(x, y, wrg, hrg, row_axis=1, col_axis=2, channel_axis=0,
                 fill_mode='nearest', cval=0.):
    """Performs a random spatial shift of a Numpy image tensor.
    # Arguments
        x: Input tensor. Must be 3D.
        wrg: Width shift range, as a float fraction of the width.
        hrg: Height shift range, as a float fraction of the height.
        row_axis: Index of axis for rows in the input tensor.
        col_axis: Index of axis for columns in the input tensor.
        channel_axis: Index of axis for channels in the input tensor.
        fill_mode: Points outside the boundaries of the input
            are filled according to the given mode
            (one of `{'constant', 'nearest', 'reflect', 'wrap'}`).
        cval: Value used for points outside the boundaries
            of the input if `mode='constant'`.
    # Returns
        Shifted Numpy image tensor.
    """
    h, w = x.shape[row_axis], x.shape[col_axis]
    tx = np.random.uniform(-hrg, hrg) * h
    ty = np.random.uniform(-wrg, wrg) * w
    translation_matrix = np.array([[1, 0, tx],
                                   [0, 1, ty],
                                   [0, 0, 1]])

    x = apply_transform_img(x, translation_matrix, channel_axis, fill_mode, cval)
    
    
    
    translation_matrix = np.array([[1, 0, -ty],
                                   [0, 1, -tx],
                                   [0, 0, 1]])
    yr = apply_transform_coord(y, translation_matrix)
    
    return x, yr


def apply_transform_coord(y, transform_matrix):
    yr = np.ones((y.shape[0],y.shape[1]+1)); 
    yr[:,:-1] = y
    yr = np.dot(transform_matrix, yr.T).T
    return yr[:, :-1]

def apply_transform_img(x,
                    transform_matrix,
                    channel_axis=0,
                    fill_mode='nearest',
                    cval=0.):
    """Apply the image transformation specified by a matrix.
    # Arguments
        x: 2D numpy array, single image.
        transform_matrix: Numpy array specifying the geometric transformation.
        channel_axis: Index of axis for channels in the input tensor.
        fill_mode: Points outside the boundaries of the input
            are filled according to the given mode
            (one of `{'constant', 'nearest', 'reflect', 'wrap'}`).
        cval: Value used for points outside the boundaries
            of the input if `mode='constant'`.
    # Returns
        The transformed version of the input.
    """
    x = np.rollaxis(x, channel_axis, 0)
    final_affine_matrix = transform_matrix[:2, :2]
    final_offset = transform_matrix[:2, 2]
    channel_images = [ndi.interpolation.affine_transform(
        x_channel,
        final_affine_matrix,
        final_offset,
        order=0,
        mode=fill_mode,
        cval=cval) for x_channel in x]
    x = np.stack(channel_images, axis=0)
    x = np.rollaxis(x, 0, channel_axis + 1)
    return x


def transform_matrix_offset_center(matrix, x, y):
    o_x = float(x) / 2 + 0.5
    o_y = float(y) / 2 + 0.5
    offset_matrix = np.array([[1, 0, o_x], [0, 1, o_y], [0, 0, 1]])
    reset_matrix = np.array([[1, 0, -o_x], [0, 1, -o_y], [0, 0, 1]])
    transform_matrix = np.dot(np.dot(offset_matrix, matrix), reset_matrix)
    return transform_matrix

def random_zoom(x, y, zoom_range, row_axis=1, col_axis=2, channel_axis=0,
                fill_mode='nearest', cval=0.):
    """Performs a random spatial zoom of a Numpy image tensor.
    # Arguments
        x: Input tensor. Must be 3D.
        zoom_range: Tuple of floats; zoom range for width and height.
        row_axis: Index of axis for rows in the input tensor.
        col_axis: Index of axis for columns in the input tensor.
        channel_axis: Index of axis for channels in the input tensor.
        fill_mode: Points outside the boundaries of the input
            are filled according to the given mode
            (one of `{'constant', 'nearest', 'reflect', 'wrap'}`).
        cval: Value used for points outside the boundaries
            of the input if `mode='constant'`.
    # Returns
        Zoomed Numpy image tensor.
    # Raises
        ValueError: if `zoom_range` isn't a tuple.
    """
    if len(zoom_range) != 2:
        raise ValueError('zoom_range should be a tuple or list of two floats. '
                         'Received arg: ', zoom_range)

    if zoom_range[0] == 1 and zoom_range[1] == 1:
        zx, zy = 1, 1
    else:
        zx, zy = np.random.uniform(zoom_range[0], zoom_range[1], 2)
    zoom_matrix = np.array([[zx, 0, 0],
                            [0, zy, 0],
                            [0, 0, 1]])

    h, w = x.shape[row_axis], x.shape[col_axis]
    transform_matrix = transform_matrix_offset_center(zoom_matrix, h, w)
    x = apply_transform_img(x, transform_matrix, channel_axis, fill_mode, cval)
    
    print(transform_matrix)
    zoom_matrix = np.array([[1/zy, 0, 0],
                            [0, 1/zx, 0],
                            [0, 0, 1]])
    transform_matrix = transform_matrix_offset_center(zoom_matrix, h, w)
    y = apply_transform_coord(y, transform_matrix)
    return x, y


if __name__ == '__main__':
    import os
    
    SAVE_DIR = '/Volumes/behavgenom_archive$/Avelino/skeletons_cnn_tests/'
    
    log_dir_n = 'tiny_resnet_20170322_191940'
    log_dir = os.path.join(SAVE_DIR, 'logs', log_dir_n)
    sample_file = os.path.join(log_dir, 'input_set.hdf5')
    with tables.File(sample_file, 'r') as fid:
        
        #select a tiny sample
        X_set = fid.get_node('/X')
        Y_set = fid.get_node('/Y')

        tot = X_set.shape[0]
        roi_size = X_set.shape[1]
        
        inds = np.random.permutation(tot)[:16]
        X = X_set[inds, :, :]
        Y = Y_set[inds, :, :]
        Y = Y*roi_size/2 + roi_size/2.
    
    #%%
    import matplotlib.pylab as plt
    xx = X[0]
    yy = Y[0]
    
    zoom_range = 0.25
    if np.isscalar(zoom_range):
        zoom_range = [1 - zoom_range, 1 + zoom_range]
    elif len(zoom_range) == 2:
        zoom_range = [zoom_range[0], zoom_range[1]]
    else:
        raise ValueError('zoom_range should be a float or '
                         'a tuple or list of two floats. '
                         'Received arg: ', zoom_range)
    
    #img, yr = random_rotation(xx, yy, 90, row_axis=0, col_axis=1, channel_axis=2)
    img, yr = random_shift(xx, yy, 0.1, 0.1, row_axis=0, col_axis=1, channel_axis=2)
    img, yr = random_rotation(img, yr, 90, row_axis=0, col_axis=1, channel_axis=2)
   
    img, yr = random_zoom(xx, yy, zoom_range, row_axis=0, col_axis=1, channel_axis=2)
    
    plt.subplot(1,2,1)
    plt.imshow(np.squeeze(xx), interpolation='none', cmap='gray')
    plt.plot(yy[:,0], yy[:,1])
    plt.plot(yy[0,0], yy[0,1], 'x')
    plt.plot()
    plt.subplot(1,2,2)
    plt.imshow(np.squeeze(img), interpolation='none', cmap='gray')
    plt.plot(yr[:,0], yr[:,1])
    plt.plot(yr[0,0], yr[0,1], 'x')
#    
#    plt.plot(yy[:,0], yy[:,1])
#    plt.plot(yy[0,0], yy[0,1], 'x')