#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 12:45:02 2025

@author: cristina
"""

'''DISCO DICOM to nifti'''

import os
import pydicom
from collections import defaultdict
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np
import dicom2nifti
import nibabel as ni
from totalsegmentator.python_api import totalsegmentator
import shutil

def sort_slices (slices_list, dir_path):
    """
    Sorts slices according to the instance numebr tag
    
    Inputs
    ---------
    slices_list: list of slices names
    dir_path: the path of the folder containing the slices from slices_list
          
    Returns
    -------
    slices_list: list of slices names ordered based on the instance number tag
    """  
    pos = []
    for sl in slices_list:
        img = pydicom.dcmread(os.path.join(dir_path, sl), force=True) #read the current slice
        pos.append(img[0x00200013].value) #save the original order of instance number
        
    sort_args = np.argsort(pos) #sort the instance numbers and save the new order of the list arguments
    slices_list[:] = [slices_list[i] for i in sort_args] #save the reordered slices names based on the instance numbers
        
    return slices_list

#%%
'''Separate all the acquisitions in a dictionary'''

input_dir = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD010/RAW/DISCOSTAR'
slices = os.listdir(input_dir)
output_dir = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD010/Processed/DISCOSTAR/DICOM'
nifti_dir = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD010/Processed/DISCOSTAR/NIFTI'

if not os.path.exists(nifti_dir):
    os.mkdir(nifti_dir)

acq_dict = defaultdict(list)
for sl in slices:
    sl_path = os.path.join(input_dir, sl)
    data = pydicom.dcmread(sl_path)
    try:
        temp_pos = data[0x00200100].value #check if the temporal position exists
    except:
        acq_dict[0].append(sl) #mask
        if not os.path.exists(os.path.join(output_dir, str(0))):
            os.makedirs(os.path.join(output_dir, str(0)))
        shutil.copy(sl_path, os.path.join(output_dir, str(0), sl))
    else:
        acq_dict[int(temp_pos)].append(sl)
        if not os.path.exists(os.path.join(output_dir, str(temp_pos))):
            os.makedirs(os.path.join(output_dir, str(temp_pos)))
        shutil.copy(sl_path, os.path.join(output_dir, str(temp_pos), sl))
folders = os.listdir(output_dir)    
for d in folders:
    nifti_name = d+'.nii'
    nifti_file = os.path.join(nifti_dir, nifti_name)
    dicom2nifti.dicom_series_to_nifti(os.path.join(output_dir, d), nifti_file, reorient_nifti=False)
    
