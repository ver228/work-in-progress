#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 13:57:07 2017

@author: ajaver
"""

import os
import glob
import pandas as pd
import numpy as np
import tables

import matplotlib.pylab as plt
from tierpsy.helper.params import read_fps
from tierpsy_features.summary_stats import _test_get_feat_stats_all

n_pulses = 5
regions = ['before', 'after', 'long_pulse']
pulses_regions = ['short_pulse_{}'.format(ii+1) for ii in range(n_pulses)]
inter_pulses_regions = ['inter_pulses_{}'.format(ii+1) for ii in range(n_pulses)]
regions += pulses_regions + inter_pulses_regions

REGION_LABELS = {x:ii for ii,x in enumerate(regions)}
#%%
#make the inverse diccionary to get the name from the index
REGION_LABELS_I = {val:key for key, val in REGION_LABELS.items()}


def read_light_data(mask_file, n_sigmas=6):
    
    with tables.File(mask_file) as fid:
        mean_intensity = fid.get_node('/mean_intensity')[:]
        timestamp = fid.get_node('/timestamp/raw')[:]
    
    med = np.median(mean_intensity)
    mad = np.median(np.abs(mean_intensity-med))
    #the MAD is releated to sigma by the factor below as explained here:
    #wiki (https://en.wikipedia.org/wiki/Median_absolute_deviation#relation_to_standard_deviation)
    s = mad*1.4826 
    
    #... and since the median should be equal to the mean in a gaussian dist
    # we can use 6 sigma as our threshold
    light_on = mean_intensity >  med + s*n_sigmas
    
    #shift data to match the timestamps (deal with possible drop frames)
    
    if ~np.all(np.isnan(timestamp)) > 0:
        timestamp = timestamp.astype(np.int)
        max_ts = np.max(timestamp)+1
        light_on_s = np.full(max_ts, np.nan)
        if light_on.size < max_ts:
            #pad if the light on vector is too small
            light_on = np.pad(light_on, (0,max_ts-light_on.size), 'edge')
        light_on_s[timestamp] = light_on[timestamp]
        light_on = light_on_s
    
    return light_on

def get_pulses_indexes(light_on, window_size):
    switches = np.diff(light_on.astype(np.int))
    turn_on, = np.where(switches==1)
    turn_off, = np.where(switches==-1)
    
    assert turn_on.size == turn_off.size
    
    delP = turn_off - turn_on
    
    good = delP>window_size/2
    
    
    return turn_on[good], turn_off[good]



def define_regions(tot_frames, turn_on, turn_off, frames_w = 15):
    regions_lab = np.zeros(tot_frames, np.int)
    
    regions_lab[:turn_on[0]-frames_w] = REGION_LABELS['before']
    regions_lab[turn_off[-1] + frames_w :] = REGION_LABELS['after']
    
    regions_lab[turn_on[-1] + 1 :turn_off[-1]] = REGION_LABELS['long_pulse']
    
    for ii in range(n_pulses):
        ini = turn_on[ii]
        fin = turn_off[ii]
        regions_lab[ini + 1 : fin] = REGION_LABELS['short_pulse_{}'.format(ii+1)]
    
    for ii in range(n_pulses):
        ini = turn_off[ii]
        fin = turn_on[ii+1]
        regions_lab[ini + 1 : fin] = REGION_LABELS['inter_pulses_{}'.format(ii+1)]
    
        
    return regions_lab

def get_exp_data(mask_dir):
    fnames = glob.glob(os.path.join(mask_dir, '**', '*.hdf5'), recursive=True)
    
    col_names = ['day', 'strain', 'exp_type', 'mask_file', 'has_valid_light', 'video_duration']
    col_names +=  [REGION_LABELS_I[x] for x in sorted(REGION_LABELS_I.keys())]
    extra_cols_v =  [False] +  [np.nan]* (len(REGION_LABELS_I) + 1)
    
    data = []
    for fname in fnames:
        day_n = fname.split(os.sep)[-2].rpartition('-')[-1]
        base_name = os.path.basename(fname).replace('.hdf5', '')
        
        strain_n, _, dd = base_name.partition('-') 
        exp_type = dd.partition('_') [0]
        
        data.append([day_n, strain_n, exp_type, fname] + extra_cols_v)
    
    
    
    df = pd.DataFrame(data, columns=col_names)
    
    
    return df

def read_file_data(mask_file, feat_file, min_pulse_size_s=3, _is_debug=False):
    
    fps = read_fps(mask_file)
    min_pulse_size = fps*min_pulse_size_s
     
    light_on = read_light_data(mask_file)
    if np.nansum(light_on) < min_pulse_size:
        return
        
    turn_on, turn_off = get_pulses_indexes(light_on, min_pulse_size)
    region_lab = define_regions(light_on.size, turn_on, turn_off)
    region_size = np.bincount(region_lab)[1:]/fps
    
    if _is_debug:
        plt.figure()
        #plt.plot(region_lab)
        plt.plot(light_on)
        plt.plot(turn_on, light_on[turn_on], 'o')
        plt.plot(turn_off, light_on[turn_off], 'x')
        plt.title(os.path.basename(mask_file))
    #read features
    with pd.HDFStore(feat_file, 'r') as fid:
        timeseries_data = fid['/timeseries_data']
        blob_features = fid['/blob_features']
        
    timeseries_data['timestamp'] = timeseries_data['timestamp'].astype(np.int)
    #label if frame with the corresponding region
    timeseries_data['region_lab'] = region_lab[timeseries_data['timestamp']]
    
    return timeseries_data, blob_features, fps, region_size

#def get_feat_stats(feat_timeseries, FRAC_MIN=0.8):
#    #columns that correspond to indexes (not really features)
#    index_cols =['worm_index','timestamp','skeleton_id','motion_modes']
#    normal_feats = [x for x in feat_timeseries.columns if not x in index_cols]
#    
#    #get the stats for each region and each feature
#    r_stats = []
#    for r_lab, r_dat in feat_timeseries.groupby('region_lab'):
#        if r_lab not in REGION_LABELS_I:
#            #likely 0 value corresponding a frames between regions
#            continue
#        
#        lab = REGION_LABELS_I[r_lab]
#            
#        for feat in normal_feats:
#            
#            feat_d = r_dat[feat]
#            q = np.nanpercentile(feat_d, [5, 50, 95])
#            frac_valid = feat_d.count()/feat_d.size
#            
#            if frac_valid > FRAC_MIN:
#                dd = [
#                (lab, feat, '5th', q[0]),
#                (lab, feat, '50th', q[1]),
#                (lab, feat, '95th', q[2])
#                ]
#            
#                r_stats += dd
#        #the motion_modes is a bit different. It is -1 if the worm is going backwards,
#        # 0 if it is paused and 1 if it is going forward
#        feat_d = r_dat['motion_modes']
#        nn = feat_d.count()
#        
#        if nn/feat_d.size > FRAC_MIN:
#            dd = [
#                (lab, 'motion_modes', 'f_backwards', np.sum(feat_d==-1)/nn),
#                (lab, 'motion_modes', 'f_paused', np.sum(feat_d==0)/nn),
#                (lab, 'motion_modes', 'f_forward', np.sum(feat_d==1)/nn)
#                    ]
#            r_stats += dd
#        
#        
#    r_stats = pd.DataFrame(r_stats, columns=['region', 'feat', 'stat', 'value'])
#    
#    return r_stats
#

#%%
#
#   
if __name__ == '__main__':
    _is_debug = True
    
    mask_dir = '/Volumes/behavgenom_archive$/Lidia/MaskedVideos'
    exp_df = get_exp_data(mask_dir)
    
    #correct some issues
    wrongly_named_stains = {'HRB222':'HBR222'}
    bad_strains = ['AZ46', 'AZ60']
    exp_df['strain'].replace( wrongly_named_stains)
    exp_df = exp_df[~exp_df['strain'].isin(bad_strains)]
    exp_df.index = np.arange(len(exp_df))
    
    #%%
    
    all_data = pd.DataFrame()
    for irow, row in exp_df.iterrows():
        print(irow+1, len(exp_df))
        mask_file = row['mask_file']
        feat_file = mask_file.replace('MaskedVideos', 'Results').replace('.hdf5', '_featuresN.hdf5')
        
        output = read_file_data(mask_file, feat_file, _is_debug = _is_debug)
        if output is None:
            continue
        else:
            timeseries_data, blob_features, fps, region_size = output
        
        exp_df.loc[irow, 'has_valid_light'] = True
        fps = read_fps(mask_file)
        exp_df.loc[irow, 'video_duration'] = timeseries_data['timestamp'].max()/fps
        #add duration of each region
        for ii, val in enumerate(region_size):
            exp_df.loc[irow, REGION_LABELS_I[ii+1]] = val
        #%%
        r_stats_l = []
        for r_lab, r_dat in timeseries_data.groupby('region_lab'):
            if r_lab not in REGION_LABELS_I:
                #likely 0 value corresponding a frames between regions
                continue
            
            lab = REGION_LABELS_I[r_lab]
            r_blob = blob_features.loc[r_dat.index]
            
            r_dat = r_dat.reset_index(drop=True)
            r_blob = r_blob.reset_index(drop=True)
            
            dd = _test_get_feat_stats_all(r_dat, r_blob, fps)
            print(r_lab)
            r_stats_l += [(r_lab, *x) for x in zip(dd.index, dd)]
        #%%
        r_stats = pd.DataFrame(r_stats_l, columns=['region', 'feat', 'value'])
            
        
        r_stats['exp_id'] = irow

        all_data = pd.concat([all_data, r_stats])
        
        if irow > 5:
            asfa
    #%%
    #save results
    all_data.to_csv('regions_stats.csv', index=False)
    exp_df.to_csv('exp_info.csv')
    