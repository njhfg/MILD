#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 08:15:23 2024

@author: cristina
"""

'''T2 mapping'''

#%% 
'''Imports'''

import pydicom
import os
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from skimage import exposure
from PIL import Image
import cv2
from matplotlib.patches import Rectangle
from natsort import natsorted

#%%
'''Functions'''

def function_linear(te,slope):
    #because the signal logarithmic
    signal = slope*te
    return signal

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

def plot_ROI_rect(roi, im_size, im):
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
#%%
'''Initialization'''

main_dir = '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15619/Propeller_BW62.5_separated'
dir_paths = os.listdir(main_dir)
dir_paths = natsorted(dir_paths) #sort in natural order
no_dirs = len(dir_paths)

for i in range(no_dirs):
    #get the paths of the subfolders corresponding to each TE
    dir_paths[i] = os.path.join(main_dir, dir_paths[i])

#te = [5.168, 25.84, 51.68] 
#TODO: write a function to extract the exact TE values from the DICOM tags
te = [10.336, 51.68]

#%%
'''Organize all the slices'''

no_slices = len(os.listdir(os.path.join(main_dir, dir_paths[0])))
slices_matrix = [] #each row is a folder containing the ordered list of slices names
#Create a list of the sorted slices names (based on instance number) for each directory
for i,d in enumerate(dir_paths):
    slices_list = os.listdir(d)
    slices_matrix.append(sort_slices(slices_list, d))
#%%
'''Getting the ROI for one slice'''

slice_no = 40
slices_list = slices_matrix[0] #the slices names list of the first folder
slice_path = os.path.join(dir_paths[0], slices_list[slice_no]) #path of the current slice
s = pydicom.dcmread(slice_path) #read the DICOM data
s_arr = s.pixel_array #get the array
roi = cv2.selectROI(s_arr)
#roi = (0, 0, 512, 512) #the whole image
mask,_, area = plot_ROI_rect(roi, s_arr.shape[0], s_arr)
data_matrix = np.zeros((no_dirs, area)) #to store the flatten ROI values for curve fitting
decay_matrix = np.zeros(no_dirs) #to store the ROI mean to plot the decay
t2_est = np.zeros((area)) #empty array for T2 values 

#%%
'''Get the data for mapping'''

for j in range(no_dirs):   
    #keep the signal intensities values in a matrix of number of folders x number of pixels per ROI
    slices_list = slices_matrix[j] #the ordered slices names list of the current folder
    slice_path = os.path.join(dir_paths[j], slices_list[slice_no]) #path of the current slice
    s = pydicom.dcmread(slice_path) #read the DICOM data
    s_arr = s.pixel_array #get the array
    _,decay_matrix[j],_ = plot_ROI_rect(roi, s_arr.shape[0], s_arr) #save the mean of ROI for the decay
    s_arr = s_arr[mask==1] #selct only the ROI from the array
    #print('Maximum array value', np.amax(s_arr))
    s_arr = s_arr.flatten()
    data_matrix[j,:] = s_arr #add the flat array to the data matrix
#%%
'''T2 mapping'''
    
for t in range(data_matrix.shape[1]): #number of pixels
    #do the curve fitting for each pixel location
    try:
        params, _ = curve_fit(function_linear, te, np.log(data_matrix[:, t]))
        t2_est[t] = 1/params[0] #because the slope is 1/T2
    except:
        pass
    
t2_est[t2_est==np.inf]=0
t2_est[t2_est>100]=0
t2_est = t2_est.reshape((roi[3], roi[2])) #ROI dimensions
t2_max = np.amax(t2_est)

#Histogram equalization
t2_eq = exposure.equalize_hist(t2_est)
t2_eq = t2_eq*t2_max #rescale the vlaues as before 
t2_eq = t2_eq.astype(np.float32)
#Plot the map
fig = plt.figure()
im = plt.imshow(t2_eq, cmap='plasma', vmin=np.amin(t2_eq), vmax=t2_max)
fig.colorbar(im)
plt.show()
#Plot the signal decay
plt.figure()
plt.plot(te, decay_matrix)
plt.title("Signal decay")
plt.show()