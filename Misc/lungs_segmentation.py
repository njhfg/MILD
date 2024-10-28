#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 12:48:24 2024

@author: cristina
"""

import dicom2nifti
import os
import nibabel as ni
import matplotlib.pyplot as plt
import numpy as np
from totalsegmentator.python_api import totalsegmentator

#%%
'''Convert DICOM to Nifti'''

input_path = '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15619/Propeller_test/TE10'
output_path = '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15619/Propeller_test/TE10.nii'

dicom2nifti.dicom_series_to_nifti(input_path, output_path, reorient_nifti=True)

#%% 
'''Run Total Segmentator'''

vol_path = '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15619/Propeller_test/TE10.nii'
total_seg_path = '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15619/Propeller_test/total_segmentations'
vessels_seg_path = '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15619/Propeller_test/vessels_segmentations'

if not os.path.exists(total_seg_path):
    os.mkdir(total_seg_path)

if not os.path.exists(vessels_seg_path):
    os.mkdir(vessels_seg_path)

totalsegmentator(vol_path, total_seg_path, task="total_mr", verbose=True)
totalsegmentator(vol_path, vessels_seg_path, task="lung_vessels", verbose=True)

#Delete the non-lungs segmentations
seg_list = os.listdir(total_seg_path)
for seg in seg_list:
    if "lung" not in seg:
        os.remove(os.path.join(total_seg_path, seg))

#%%
'''Create the masks'''

vol = ni.load(vol_path)
vol = np.asarray(vol.dataobj)
vol = np.rot90(vol, k=3)
plt.imshow(vol[:,:, 50])
plt.show()

left_lung = ni.load(os.path.join(total_seg_path, "lung_left.nii.gz"))
left_lung = np.asarray(left_lung.dataobj)
left_lung = np.rot90(left_lung, k=3)

right_lung = ni.load(os.path.join(total_seg_path, "lung_right.nii.gz"))
right_lung = np.asarray(right_lung.dataobj)
right_lung = np.rot90(right_lung, k=3)

mask = np.zeros(vol.shape)
mask[left_lung==1] = 1 
mask[right_lung==1] = 1
plt.imshow(mask[:,:, 50])
plt.show()

#Overlay and extract the lungs
seg_lungs = vol*mask
plt.imshow(seg_lungs[:,:, 50])
plt.show()
