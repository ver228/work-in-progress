# -*- coding: utf-8 -*-
"""
Created on Tue Sep  6 17:17:43 2016

@author: ajaver
"""
import os
import numpy as np
import pandas as pd

from sqlalchemy import create_engine
from MWTracker.featuresAnalysis.obtainFeaturesHelper import WormStatsClass

    
def convertUnits(df, microns_per_pixel):
    
    def _removeExtra(x):
        for bad_str in ['_pos', '_neg', '_abs', '_paused', '_foward', '_backward']:
            x = x.replace(bad_str, '')
        return x
    
    dict_units = WormStatsClass().features_info['units'].to_dict()
    
    def _getFactor(x):
        try:
            units = dict_units[_removeExtra(x)]
        except KeyError:
            units = '1'
        if units in ['microns', 'microns/seconds']:
            return microns_per_pixel
        elif units == 'microns^2':
            return microns_per_pixel**2
        elif units == 'radians/microns':
            return 1/microns_per_pixel
        else:
            return 1
    
    for feat in df:
        df[feat] *= _getFactor(feat)
    
    return df
    
class ReadFeaturesHDF5(object):
    def __init__(self):
        self.ws = WormStatsClass()
    
    def get(self, features_file, feat2read = []):
        if not feat2read:
            feat2read = self.ws.feat_timeseries
        feat2read = ['worm_index', 'timestamp'] + feat2read
        with pd.HDFStore(features_file, 'r') as fid:
            features_timeseries = fid['/features_timeseries']
            features_timeseries = features_timeseries[feat2read]

        return features_timeseries
    
    def get_means(self, features_file, group_str = 'feat_means'):
        with pd.HDFStore(features_file, 'r') as fid:
            features_means = fid['/' + group_str]
        return features_means

        
def get_path_df_control(file_list, main_dir):
    
    experiments_data = pd.read_csv('controlset_experiments.csv')
    dictR2P = {(row['base_name'], row['channel']):i for i, row in experiments_data.iterrows()}
    
    def _split_fname_fun(fname):
        subdir_name, base_name = fname.replace(main_dir, '').split(os.path.sep) 
        base_name = base_name.replace('_features.hdf5', '')
        
        exp_timestamp = pd.to_datetime(subdir_name.partition('_')[-1], format='%d%m%Y_%H%M')
        
        channel_str, _, timestamp_str = base_name.partition('_')[-1].partition('_')
        vid_timestamp = pd.to_datetime(timestamp_str, format='%d%m%Y_%H%M%S')
        
        row_key = (subdir_name, channel_str)
        _, _, strain, focus = experiments_data.ix[dictR2P[row_key]].values

        # calibration:  micrometer/pixel = -0.1937*(camera focus)+13.4377
        microns_per_pixel = -0.1937*(focus)+13.4377
        
        exp_delta = (vid_timestamp - exp_timestamp)/np.timedelta64(1, 'm')
        
        return base_name, channel_str, exp_timestamp, vid_timestamp, exp_delta, \
                    strain, focus, microns_per_pixel, fname
        
        
    DD_tup = zip(*map(_split_fname_fun, file_list))
    colnames = ['base_name', 'channel', 'experiment_timestamp', 'video_timestamp',
                'experiment_delta', 'strain', 'focus', 'microns_per_pixel',
                'full_name']
    DD = pd.DataFrame({col:dat for col, dat in zip(colnames, DD_tup)})
    
    return DD

def saveIntoDB(database_name, experiments):
    
    assert all(x in experiments for x in ['full_name', 'microns_per_pixel'])
    
    disk_engine = create_engine('sqlite:///' + database_name)
    experiments.to_sql('experiments', 
                       disk_engine, 
                       if_exists='replace', 
                       index_label = 'video_id')
    
    feat_reader = ReadFeaturesHDF5()
    for video_id, plate_row in experiments.iterrows():
        if not os.path.exists(plate_row['full_name']):
                continue
            
        for feat_str in ['features_means', 'features_means_split']:
            plate_mean_features = feat_reader.get_means(plate_row['full_name'], feat_str)
            plate_mean_features = convertUnits(plate_mean_features, plate_row['microns_per_pixel'])
            plate_mean_features['video_id'] = video_id
    
            exists_type = 'replace' if video_id == 0 else 'append'
            plate_mean_features.to_sql(feat_str, 
                                  disk_engine,
                                  if_exists=exists_type,
                                  index = False)
            
        print(plate_row['base_name'])
    
#plate_mean_features
if __name__ == '__main__':
    main_dir = '/Volumes/behavgenom_archive$/Avelino/GeckoVideo/Results/ControlSet_(N2-unc9-trp5)/'
    
    #all_feat_list = glob.glob(os.path.join(main_dir, '*/*_features.hdf5'))
    with open('controlset_feat_list.txt', 'r') as fid:
        all_feat_list = [x for x in fid.read().split('\n') if x]
    
    database_dir = '/Users/ajaver/OneDrive - Imperial College London/compare_strains_DB'
    database_name = os.path.join(database_dir, 'control_experiments.db')
    
    experiments = get_path_df_control(all_feat_list, main_dir)
    
    plate_tuples = sorted(set((x['experiment_timestamp'], x['channel']) for ii, x in experiments.iterrows()))
    plate_dicts = {x:i for i,x in enumerate(plate_tuples)}
    experiments['plate_id'] = [plate_dicts[(x['experiment_timestamp'], x['channel'])] for ii, x in experiments.iterrows()]
                   
    saveIntoDB(database_name, experiments)
    

    
    