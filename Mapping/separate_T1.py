#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 07:39:49 2024

@author: cristina
"""

'''Separate the T1 based on the time they were acquired (pre contrast, 1 min, 5 min and 10 min)
Then separate these based on the flip angle (10, 6, 2)'''

#%%
'''Imports'''
import os
import pydicom
import numpy as np

def sort_slices (slices_list, dir_path):
    '''Sort slices according to the instance numebr tag'''
    pos = []
    for sl in slices_list:
        img = pydicom.dcmread(os.path.join(dir_path, sl), force=True) #read the current slice
        pos.append(img[0x00200013].value) #save the original order of instance number
        
    sort_args = np.argsort(pos) #sort the instance numbers and save the new order of the list arguments
    slices_list[:] = [slices_list[i] for i in sort_args] #save the reordered slices names based on the instance numbers
        
    return slices_list

#%%
'''Separate based on the acquisition time'''
main_dir = r'/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD003/RAW/T1_mapping'
dir_list = os.listdir(main_dir)
acq_time_list = []
for d in dir_list:
    first_slice_path = os.listdir(os.path.join(main_dir, d))[0]
    first_slice = pydicom.dcmread(os.path.join(main_dir, d, first_slice_path))
    acq_time_list.append(int(first_slice[0x00080031].value)) #Series Time tag
    
new_dir_names = ['T1map_0', 'T1map_1', 'T1map_5', 'T1map_10']
sort_args = np.argsort(acq_time_list)

for i in range(4):
    old_path = os.path.join(main_dir, dir_list[sort_args[i]])
    new_path = os.path.join(main_dir, new_dir_names[i])
    os.rename(old_path, new_path)

#%%
'''Separate based on the creation time'''

dir_list = os.listdir(main_dir) #list of directories with the new names
for d in dir_list:
    dir_path = os.path.join(main_dir, d)
    slices_list = os.listdir(dir_path)
    slices_list = sort_slices(slices_list, dir_path)
    
    slice1 = pydicom.dcmread(os.path.join(dir_path, slices_list[0]))
    time1 = int(slice1[0x00080032].value)
    
    slice2 = pydicom.dcmread(os.path.join(dir_path, slices_list[300]))
    time2 = int(slice2[0x00080032].value)
    
    slice3 = pydicom.dcmread(os.path.join(dir_path, slices_list[600]))
    time3 = int(slice3[0x00080032].value)    
    ls = []
    for sl in slices_list:
        sl_path = os.path.join(dir_path, sl)
        s = pydicom.dcmread(sl_path)
        acq_time = int(s[0x00080032].value) #acquisition time
        ls.append(acq_time)
        if acq_time==time1:
            if not os.path.exists(os.path.join(dir_path,'FA10')):
                os.mkdir(os.path.join(dir_path, 'FA10'))
            os.replace(os.path.join(dir_path,sl), os.path.join(dir_path, 'FA10', sl))
        elif acq_time==time2:
            if not os.path.exists(os.path.join(dir_path, 'FA6')):
                os.mkdir(os.path.join(dir_path, 'FA6'))
            os.replace(os.path.join(dir_path,sl), os.path.join(dir_path, 'FA6', sl))
        else:
            if not os.path.exists(os.path.join(dir_path, 'FA2')):
                os.mkdir(os.path.join(dir_path, 'FA2'))
            os.replace(os.path.join(dir_path,sl), os.path.join(dir_path, 'FA2', sl))
