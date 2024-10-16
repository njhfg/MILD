#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 11:52:09 2023

@author: Cristina
"""

'''For Ieva'''

import pydicom
import numpy as np
import os
import matplotlib.pyplot as plt
from PIL import Image
from pydicom.pixel_data_handlers.util import apply_modality_lut

#%%
'''Funtions'''
def normalize(m, r_min, r_max, t_min, t_max):
    '''Normalization between 2 values
    Args: m - current value to be normalized
    r_min, r_max - initial range minimum and maximum
    t-min, t_max - desired range minimum and maximum'''
    r_range = r_max-r_min
    t_range = t_max-t_min
    return ((m-r_min)/r_range)*t_range+t_min

def sort_slices (slices, input_dir_path):
    '''Sort slices according to the Instance number tag'''
    pos = []
    for sl in slices:
        img = pydicom.dcmread(os.path.join(input_dir_path, sl), force=True) #read the current slice 
        pos.append(img[0x00200013].value) #save the original order of instance numbers
    
    sort_args = np.argsort(pos) #sort the instance numbers
    slices[:] = [slices[i] for i in sort_args] #reorder the slices according to the ascending order of instance numbers
    
    return slices #the reordered slices
#%%    
patient_path = '/home/cristina/mrpg_share2/Cristina/Ieva/CF_patient_2_organized/Exp'
save_dir = '/home/cristina/mrpg_share2/Cristina/Ieva/CF_patient_cut/Exp'

patient_dir_ls = os.listdir(patient_path)

#patient_dir_ls = patient_dir_ls[0:1]

zone = '2'

for d in patient_dir_ls:
    
    dcm_slices = os.listdir(os.path.join(patient_path, d))
    dcm_slices = sort_slices(dcm_slices, os.path.join(patient_path, d))
    
    sl_t = d.split("_")[1] #slice thickness from the folder name
    sl_k = d.split("_")[0] #kernel from the folder name
    
    #Choose the slice number
    if sl_t=='0.2':
        sl_no = 496
    elif sl_t=='0.6':
        sl_no = 166
    elif sl_t=='1':
        sl_no = 100
            
    #Read the slice
    sl = pydicom.dcmread(os.path.join(patient_path, d, dcm_slices[sl_no]))
    sl_array = sl.pixel_array
    
    #plt.imshow(sl_array)
    #plt.show()
    
    #Change the window and level to fit the lungs
    out = apply_modality_lut(sl_array, sl)

    #sl_description = sl[0x0008103e].value
    kernel = sl[0x00181210].value
    sl_thickness = sl[0x00180050].value
    sl_rows = sl[0x00280010].value
    #x and y are swapped form how they are in the Excel file    
    
    if sl_rows == 768:
        x_left = 293
        y_left = 477
        width = 175
        height = 175
    else:
        x_left = 391
        y_left = 636
        width = 233
        height = 233

    
    ST = str(sl_thickness)
    KT = kernel[0][0:2]
    KR = kernel[0][2:4]
    #RM = sl_description[-2:]
    
    #name = 'Z'+zone+'_'+KT+KR+'_'+ST+'_'+RM+'.tif'
    name = 'Z'+zone+'_'+KT+KR+'_'+ST+'.tif'
 
    clipping = out[x_left:x_left+width, y_left:y_left+height]
    c_min = np.amin(clipping)
    c_max = np.amax(clipping)
    
    clipping = clipping.astype(np.float32)

    
    im = Image.fromarray(clipping)
    im.save(os.path.join(save_dir, name), format='TIFF')


