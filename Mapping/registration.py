#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 10:05:16 2024

@author: cristina
"""

#TODO: Convert back to DICOM by replacing the pixel data with the registered one. Convert nifti to array before. 
#TODO: Write the registration in a function 

import dicom2nifti
import os
import nibabel as ni
import matplotlib.pyplot as plt
import numpy as np
import itk
import SimpleITK as sitk

def create_mask (seg_path):
    left_lung = ni.load(os.path.join(seg_path, "lung_left.nii.gz"))
    left_lung = np.asarray(left_lung.dataobj, np.uint8)
    left_lung = np.rot90(left_lung, k=3)

    right_lung = ni.load(os.path.join(seg_path, "lung_right.nii.gz"))
    right_lung = np.asarray(right_lung.dataobj, np.uint8)
    right_lung = np.rot90(right_lung, k=3)

    mask = np.zeros(left_lung.shape, np.uint8)
    mask[left_lung==1] = 1 
    mask[right_lung==1] = 1
    
    mask = itk.image_view_from_array(mask)

    return mask


#%%
'''DICOM to Nifti'''

fixed_dicom_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD003/RAW/T1_mapping/T1map_0/FA2'
moving_dicom_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD003/RAW/T1_mapping/T1map_0/FA6'
fixed_nifti_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD003/Processed/T1_mapping/T1map_0/FA2/FA2.nii'
moving_nifti_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD003/Processed/T1_mapping/T1map_0/FA6/FA6.nii'
dicom2nifti.dicom_series_to_nifti(fixed_dicom_path, fixed_nifti_path, reorient_nifti=False)
dicom2nifti.dicom_series_to_nifti(moving_dicom_path, moving_nifti_path, reorient_nifti=False)

#%%
'''Paths'''

fixed_image = itk.imread(fixed_nifti_path, itk.F)
moving_image = itk.imread(moving_nifti_path, itk.F)

saving_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD003/Processed/T1_mapping/T1map_0/FA6'

#%%
'''Rigid registration'''

parameter_object = itk.ParameterObject.New() #open a new object for paramters
default_rigid_parameter_map = parameter_object.GetDefaultParameterMap('rigid')
parameter_object.AddParameterMap(default_rigid_parameter_map)
name_result = 'FA6_reg_rigid.nii'

result_image, result_transform_parameters = itk.elastix_registration_method(
    fixed_image, moving_image,
    parameter_object=parameter_object,
    log_to_console=True)

#array = itk.GetArrayFromImage(result_image)
#plt.imshow(array[60,:,:])
#plt.show
itk.imwrite(result_image, os.path.join(saving_path, name_result))

#%%
'''Bspline registration'''

parameter_object = itk.ParameterObject.New() #open a new object for paramters
default_bspline_parameter_map = parameter_object.GetDefaultParameterMap('bspline')
parameter_object.AddParameterMap(default_bspline_parameter_map)
name_result = 'FA6_reg_bspline.nii'

result_image, result_transform_parameters = itk.elastix_registration_method(
    fixed_image, moving_image,
    parameter_object=parameter_object,
    log_to_console=True)

itk.imwrite(result_image, os.path.join(saving_path, name_result))

#%%
'''Masked bspline registration'''

seg_path_fixed = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD003/Processed/T1_mapping/T1map_0/FA2/total_segmentations'
seg_path_moving = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD003/Processed/T1_mapping/T1map_0/FA6/total_segmentations'

fixed_mask = create_mask(seg_path_fixed)
moving_mask = create_mask(seg_path_moving)

parameter_object = itk.ParameterObject.New() #open a new object for paramters
default_bspline_parameter_map = parameter_object.GetDefaultParameterMap('bspline')
parameter_object.AddParameterMap(default_bspline_parameter_map)
name_result = 'FA6_reg_bspline_masked.nii'

result_image, result_transform_parameters = itk.elastix_registration_method(
    fixed_image, moving_image,
    parameter_object=parameter_object,
    fixed_mask=fixed_mask,
    moving_mask=moving_mask,
    log_to_console=True)

itk.imwrite(result_image, os.path.join(saving_path, name_result))

#%%
'''Group-wise registration ITK'''

fixed_image = itk.imread(fixed_nifti_path, itk.F)
moving_image = itk.imread(moving_nifti_path, itk.F)
fixed_image = itk.GetArrayViewFromImage(fixed_image)
moving_image = itk.GetArrayViewFromImage(moving_image)



array_of_images = np.zeros([2, 230, 512, 512], np.float32)
array_of_images[0] = fixed_image
array_of_images[1] = moving_image

image_4d = itk.image_view_from_array(array_of_images)

param_file_path = '/home/cristina/mrpg_share2/Cristina/Scripts/par_groupwise_Rigid_2resolutions.txt'

parameter_object = itk.ParameterObject.New()
groupwise_parameter_map = parameter_object.GetDefaultParameterMap('groupwise')
ext_parameter_map = parameter_object.ReadParameterFile(param_file_path)

parameter_object.AddParameterMap(groupwise_parameter_map)
parameter_object.AddParameterMap(ext_parameter_map)


result_image, result_transform_parameters = itk.elastix_registration_method(image_4d, image_4d, parameter_object, log_to_console=True)

#%%
'''Group-wise registration SimpleITK'''
logsDirectory = '/home/cristina/mrpg_share2/Cristina/Scripts/'
population = [fixed_nifti_path, moving_nifti_path]
vectorOfImages = sitk.VectorOfImage()
for filename in population:
    vectorOfImages.push_back(sitk.ReadImage(filename))
    
image = sitk.JoinSeries(vectorOfImages)

elastixImageFilter = sitk.ElastixImageFilter()
elastixImageFilter.SetFixedImage(image)
elastixImageFilter.SetMovingImage(image)
ext_parameter_map = sitk.ReadParameterFile(param_file_path)

elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap('groupwise'))
elastixImageFilter.AddParameterMap(ext_parameter_map)

elastixImageFilter.LogToConsoleOn()
elastixImageFilter.LogToFileOn()
elastixImageFilter.SetOutputDirectory(logsDirectory)
elastixImageFilter.PrintParameterMap()
result = elastixImageFilter.Execute()