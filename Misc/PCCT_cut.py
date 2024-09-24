# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 11:52:09 2023

@author: Cristina
"""

import pydicom
import numpy as np
import os
#import matplotlib.pyplot as plt
from PIL import Image
from pydicom.pixel_data_handlers.util import apply_modality_lut

def normalize(m, r_min, r_max, t_min, t_max):
    '''Normalization between 2 values
    Args: m - current value to be normalized
    r_min, r_max - initial range minimum and maximum
    t-min, t_max - desired range minimum and maximum'''
    r_range = r_max-r_min
    t_range = t_max-t_min
    return ((m-r_min)/r_range)*t_range+t_min

def window_level(m, c, w, t_min, t_max):
    o = ((m-(c-0.5))/(w-1)+0.5)*(t_max-t_min)+t_min
    
    #o = np.zeros((m.shape[0], m.shape[1]))
    bool_array = m<=(c-0.5-(w-1)/2)
    o[bool_array] = t_min
    
    bool_array = m>(c-0.5+(w-1)/2)
    o[bool_array] = t_max
    
    return o
    
    '''
    if all(m<=(c-0.5-(w-1)/2)):
        return t_min
    elif m>(c-0.5+(w-1)/2):
        return t_max
    else:
        return ((m-(c-0.5))/(w-1)+0.5)*(t_max-t_min)+t_min
    '''
    
patient_path = r'E:\1_MILD_Study_PCCT_data\PCCT_DATA\ILD_02_Ddir\DICOM_organized'
save_dir = r'E:\1_MILD_Study_PCCT_data\PCCT_DATA\ILD_02_Ddir/cut'

patient_dir_ls = os.listdir(patient_path)

zone = '1'

temp_d = [9,10,11,18,19,20]

for i in temp_d:
    
    d = patient_dir_ls[i]
    
    dcm_slices = os.listdir(os.path.join(patient_path, d))

    sl_t = d.split("_")[1] #slice thickness from the folder name
    sl_k = d.split("_")[0]
    
    if 'Bl' in sl_k:
        if sl_t=='0.2':
            sl_no = 543
        elif sl_t=='0.6':
            sl_no = 217
        elif sl_t=='1':
            sl_no = 136
    else:
        if sl_t=='0.2':
            sl_no = 666
        elif sl_t=='0.6':
            sl_no = 267
        elif sl_t=='1':
            sl_no = 167
            
    
    sl_t = d.split("_")[1] #slice thickness from the folder name
    sl_k = d.split("_")[0]
    
    sl = pydicom.dcmread(os.path.join(patient_path, d, dcm_slices[sl_no]))
    sl_array = sl.pixel_array
    out = apply_modality_lut(sl_array, sl)
    out_min = np.amin(out)
    out_max = np.amax(out)
    w = out_max-out_min
    c = out_min+(out_max-out_min)/2
    t_min = -1200
    t_max = 0
    final = window_level(out,c,w,t_min,t_max)
    #sl_array_lungs = window_level(sl_array, -400, 1200, np.amin(sl_array), np.amax(sl_array))
    sl_description = sl[0x0008103e].value
    kernel = sl[0x00181210].value
    sl_thickness = sl[0x00180050].value
    sl_rows = sl[0x00280010].value
        
    if sl_rows == 768:
        x_left = 345
        y_left = 83
        width = 225
        height = 225
    else:
        x_left = 460
        y_left = 111
        width = 300
        height = 300

    
    ST = str(sl_thickness)
    KT = kernel[0][0:2]
    KR = kernel[0][2:4]
    RM = sl_description[-2:]
    
    name = 'Z'+zone+'_'+KT+KR+'_'+ST+'_'+RM+'.tif'
    #name='test.tif'
    clipping = out[x_left:x_left+width, y_left:y_left+height]
    c_min = np.amin(clipping)
    c_max = np.amax(clipping)
    w = c_max-c_min
    c = c_min+(c_max-c_min)/2
    #clipping = window_level(clipping, c,w,t_min,t_max)
    #clipping = normalize(clipping, np.amin(clipping), np.amax(clipping), -1000, 200)
    clipping = clipping.astype(np.float32)
    #sl_array_lungs = sl_array_lungs.astype(np.float32)

    
    im = Image.fromarray(clipping)
    im.save(os.path.join(save_dir, name), format='TIFF')
