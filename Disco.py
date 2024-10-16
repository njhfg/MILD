#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 13:50:36 2024

@author: cristina
"""

'''DICO STAR dynamic contrast-enhanced acquisition'''

import os
import pydicom
from collections import defaultdict
import cv2
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np

def plot_ROI_rect(roi, im_size, im, plot=True):
    """
    Overlays a red rectangle over an image
    
    Inputs
    ---------
    roi: the roi coordinates from the user selection
    im_size: the size of the image
    im: the image to show
    
    Returns
    -------
    mask: image with same size as the original withe 1's values only in ROI and 0 the rest'
    mean: the mean of the ROI
    area: the area of the ROI in pixels

    """
    if plot:
        rect = Rectangle((roi[0], roi[1]), roi[2], roi[3], color='r')
        fig, ax = plt.subplots() 
        ax.imshow(im)
        ax.add_patch(rect)
        plt.show()
    
    mask = np.zeros((im_size, im_size))
    mask[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]] = 1
    #print('ROI mean', np.mean(im[mask==1]))
    mean = np.mean(im[mask==1])
    area = np.count_nonzero(mask)
    return mask, mean, area


dir_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD002/RAW/Disco_Star'
slices = os.listdir(dir_path)

#%%
'''Separate all the acquisitions in a dictionary'''
acq_dict = defaultdict(list)
for sl in slices:
    sl_path = os.path.join(dir_path, sl)
    data = pydicom.dcmread(sl_path)
    try:
        temp_pos = data[0x00200100].value #check if the temporal position exists
    except:
        acq_dict['Mask'].append(sl)
    else:
        acq_dict[str(temp_pos)].append(sl)

#%%
'''Plot the contrast enhanced curve in one slice'''
#Select the 35th slice from the mask and select a ROI with cv2
mask_sl = pydicom.dcmread(os.path.join(dir_path, acq_dict['Mask'][35]))
mask_arr = mask_sl.pixel_array
#roi = cv2.selectROI(mask_arr)
roi = [139, 116, 10, 10]
mask,_, area = plot_ROI_rect(roi, mask_arr.shape[0], mask_arr)
dynamic_curve = np.zeros(len(acq_dict.keys())-1)
#Use the ROI as a mask to get the mean from each time point
for key in acq_dict:
    if key!='Mask':
        time_point = pydicom.dcmread(os.path.join(dir_path, acq_dict[key][35]))
        time_point_arr = time_point.pixel_array
        #time_point_arr = time_point_arr - mask_arr
        _,mean,_ = plot_ROI_rect(roi, time_point_arr.shape[0], time_point_arr, plot=False)
        dynamic_curve[int(key)-1] = mean
#Save the mean in an array and plot it
plt.plot(dynamic_curve)
plt.show()
