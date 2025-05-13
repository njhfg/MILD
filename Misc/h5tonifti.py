#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 12:21:16 2025

@author: cristina
"""

'''Visualize h5 images'''

import h5py
import os
import nibabel as nib
import numpy as np

file_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD008/Processed/Paris/images_raw_32gates.h5'
output_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD008/Processed/Paris/images_raw_32gates'

if not os.path.exists(output_path):
    os.mkdir(output_path)

#Extractthe data as array
with h5py.File(file_path, "r") as f:
    # Print all root level object names (aka keys) 
    # these can be group or dataset names 
    print("Keys: %s" % f.keys())
    # get first object name/key; may or may NOT be a group
    a_group_key = list(f.keys())[0]

    # get the object type for a_group_key: usually group or dataset
    print(type(f[a_group_key])) 

    # If a_group_key is a group name, 
    # this gets the object names in the group and returns as a list
    data = list(f[a_group_key])

    # If a_group_key is a dataset name, 
    # this gets the dataset values and returns as a list
    data = list(f[a_group_key])
    # preferred methods to get dataset values:
    ds_obj = f[a_group_key]      # returns as a h5py dataset object
    ds_arr = f[a_group_key][()]  # returns as a numpy array
    
#Save the arrays as Nifti files
no_images = ds_arr.shape[-1]

for i in range(no_images):
    arr = ds_arr[:,:,:,i]
    arr = np.array(arr, dtype=np.float32)
    arr = np.rot90(arr, 1)
    name = 'phase_'+str(i+1)+'.nii'
    nii_image = nib.Nifti1Image(arr, affine=np.eye(4))
    nib.save(nii_image, os.path.join(output_path, name))
    