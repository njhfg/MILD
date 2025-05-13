#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 14:33:02 2024

@author: cristina
"""

'''T1 mapping'''

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
#%%
'''Functions'''

def function_linear(x_data,slope):
    signal = slope*x_data
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
#main_dir = r'/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD004/RAW/T1_mapping/T1map_5'
def main(main_dir):
    
    dir_paths = os.listdir(main_dir) #FA dirs
    no_dirs = len(dir_paths)
    
    for i in range(no_dirs):
        #get the paths of the subfolders corresponding to each TE
        dir_paths[i] = os.path.join(main_dir, dir_paths[i])
    dir_paths.reverse() #FA10,6,2
    
    fa = [10, 6, 2] #flip angle list
    #fa = [2, 6, 10] #flip angle list
#%%    
    '''Organize all the slices'''
    
    no_slices = len(os.listdir(os.path.join(main_dir, dir_paths[0])))
    slices_matrix = [] #each row is a folder (FA10, FA6 or FA2) containing the ordered list of slices names
    #Create a list of the sorted slices names (based on instance number) for each directory
    for i,d in enumerate(dir_paths):
        slices_list = os.listdir(d)
        slices_matrix.append(sort_slices(slices_list, d))  
        
#%%
    '''Getting the ROI for one slice'''
    
    slice_no = 50
    slices_list = slices_matrix[0] #the slices names list of the first folder
    slice_path = os.path.join(dir_paths[0], slices_list[slice_no]) #path of the current slice
    s = pydicom.dcmread(slice_path) #read the DICOM data
    s_arr = s.pixel_array #get the array
    TR = s[0x00180080].value #in ms
    roi = (100, 100, 300, 300) #select the whole lungs
    #roi = cv2.selectROI(s_arr)
    mask,_, area = plot_ROI_rect(roi, s_arr.shape[0], s_arr)
    data_matrix = np.zeros((no_dirs, area)) #to store the flatten ROI values for curve fitting
    decay_matrix = np.zeros(no_dirs) #to store the ROI mean to plot the decay
    t1_est = np.zeros((area)) #empty array for T1 values 
        
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
        s_arr = s_arr.flatten()
        data_matrix[j,:] = s_arr #add the flat array to the data matrix
        
#%%
    '''T1 mapping'''
        
    for t in range(data_matrix.shape[1]): #number of pixels
        #perform the curve fitting for each pixel location
        try:
            y_data = data_matrix[:, t]/np.sin(np.deg2rad(fa))
            x_data = data_matrix[:, t]/np.tan(np.deg2rad(fa))
            params, _ = curve_fit(function_linear, x_data, y_data)
            t1_est[t] = TR/np.log(params[0]) #because the slope is e^(-TR/T1)
        except:
            pass
        
    #To test the fit
    t = 22346 #pick a random index
    y_data = data_matrix[:, t]/np.sin(np.deg2rad(fa))
    x_data = data_matrix[:, t]/np.tan(np.deg2rad(fa))
    params, _ = curve_fit(function_linear, x_data, y_data)
    slope = np.ones(3)*params
    result = function_linear(x_data, slope)
    plt.plot(x_data, y_data, 'r', label='measured curve')
    plt.plot(x_data, result, 'g', label='fitted curve')
    plt.legend()
    plt.show()
        

    t1_est = t1_est.reshape((roi[3], roi[2])) #ROI dimensions
    t1_max = np.amax(t1_est)
    
    #Plot the T1 map
    fig = plt.figure()
    im = plt.imshow(t1_est, cmap='plasma')
    fig.colorbar(im)
    plt.show()
    #Plot the signal decay
    plt.figure()
    plt.plot(fa, decay_matrix)
    plt.title("Signal decay")
    plt.show()
    
    return t1_est
if __name__ == "__main__":
    main()