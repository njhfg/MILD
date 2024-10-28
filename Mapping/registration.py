#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 10:05:16 2024

@author: cristina
"""

#TODO: Convert back to DICOM by replacing the pixel data with the registered one. Convert nifti to array. 

import dicom2nifti
import os
import nibabel as ni
import matplotlib.pyplot as plt
import numpy as np
import itk

#%%
fixed_dicom_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD003/RAW/T1_mapping/T1map_0/FA2'
moving_dicom_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD003/RAW/T1_mapping/T1map_0/FA6'
fixed_nifti_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD003/Processed/T1_mapping/T1map_0/FA2/FA2.nii'
moving_nifti_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD003/Processed/T1_mapping/T1map_0/FA6/FA6.nii'
dicom2nifti.dicom_series_to_nifti(fixed_dicom_path, fixed_nifti_path, reorient_nifti=True)
dicom2nifti.dicom_series_to_nifti(moving_dicom_path, moving_nifti_path, reorient_nifti=True)

#%%


fixed_image = itk.imread(fixed_nifti_path, itk.F)
moving_image = itk.imread(moving_nifti_path, itk.F)

parameter_object = itk.ParameterObject.New()
default_rigid_parameter_map = parameter_object.GetDefaultParameterMap('rigid')
parameter_object.AddParameterMap(default_rigid_parameter_map)

result_image, result_transform_parameters = itk.elastix_registration_method(
    fixed_image, moving_image,
    parameter_object=parameter_object,
    log_to_console=False)

array = itk.GetArrayFromImage(result_image)
plt.imshow(array[:,:,120])
plt.show()