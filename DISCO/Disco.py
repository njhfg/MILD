#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 13:50:36 2024

@author: cristina
"""

'''DISCO STAR dynamic contrast-enhanced acquisition'''

import os
import pydicom
from collections import defaultdict
import cv2
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np
import scipy as scp
from scipy.optimize import curve_fit
from scipy import stats



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
    mean = np.mean(im[mask==1])
    area = np.count_nonzero(mask)
    return mask, mean, area


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

def find_sign_change(start, stop, curve):
    current_curve = curve[start:stop]
    first_der = np.diff(current_curve)
    for i in range(1,len(first_der)):
        current = first_der[i]
        prev = first_der[i-1]
        if np.sign(current)!=np.sign(prev):
            break
    return start+i

def find_t_zero(curve):
    """
    Find the point where the curve begins to grow. Take the second derivative and find the first time 
    where the switch from positive to negative is happening and where the sqitched number is higher than a 
    threshold (ex. 5)
    
    Inputs
    -------
    curve - the median filtered curve 
    
    Returns
    -------
    t_zero - the time when the curve begins to grow 

    """
    first_der = np.diff(curve) #first derivative
    #second_der = np.diff(first_der) #second derivative
    
    #for n in range(1, len(second_der)):
        #current = second_der[n]
        #prev = second_der[n-1]
        #if np.sign(current) != np.sign(prev) and abs(current)-abs(prev)>=3:
        #if abs(current)-abs(prev)>=3:
            #t_zero = n
            #break
            #Finds the first position where the first derivative is larger than 1
    t_zero = np.argmax(~(first_der<1)) #True where first derivative is lower than 1; ~ negates.  
    
    
    return t_zero

def linear(x_data,slope):
    y_data = slope*x_data
    return y_data

def slope_intercept (start, stop, curve):
    return 0

def parameters (curve, t_zero):
    '''
    Calculate the enhancement curve parameters.

    Parameters
    ----------
    curve : float 64
        the median filtered curve
    t_zero : int
        the time when the curve begins to grow

    Returns
    -------
    m: 
        maximum value of the curve
    me: 
        maximum enhancement = (max - baseline)/baseline 
        baseline is the median of the signal before t_zero
    ttp:
        time to peak = t_max - t_zero
    wis:
        wash-in slope = arctan(a) where a is determined by fitting the linear function I=at+b 
        on the signal intensity values where t is between t_zero and t_max
    wos: 
        wash-out slope = same as wis, but t is in between t_max and t_end
    '''
    m = np.amax(curve)
    baseline = np.median(curve[0:t_zero])
    me = (m-baseline)/baseline
    max_time = np.argmax(curve)
    ttp = max_time - t_zero
    
    #Wash in slope 
    x_data_a = np.linspace(t_zero, max_time, num=max_time-t_zero+1, dtype=int)
    y_data_a = curve[x_data_a]
    params_a = stats.linregress(x_data_a, y_data_a)
    slope_a = params_a[0]
    intercept_a = params_a[1]
    #params, _ = curve_fit(linear, x_data, y_data)
    
    
    in_point = find_sign_change(max_time, len(curve), curve) #inflection point
    #Wash out slope
    x_data_d = np.linspace(max_time, in_point, num=in_point-max_time+1, dtype=int)
    y_data_d = curve[x_data_d]
    params_d = stats.linregress(x_data_d, y_data_d)
    slope_d = params_d[0]
    intercept_d = params_d[1]
    #params, _ = curve_fit(linear, x_data, y_data)
    
    find_sign_change(max_time, len(curve), curve)
    
    
    return m, me, ttp
    
dir_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD010/RAW/DISCOSTAR'
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
        acq_dict[0].append(sl) #mask
    else:
        acq_dict[int(temp_pos)].append(sl)

#%%
'''Plot the contrast enhanced curve in one slice'''
sl_no = 35
mask_slices_list = sort_slices(acq_dict[0], dir_path)
mask_sl = pydicom.dcmread(os.path.join(dir_path, mask_slices_list[sl_no]))
mask_arr = mask_sl.pixel_array
roi = [170, 150, 10, 10]
#roi = cv2.selectROI(mask_arr)
mask,_, area = plot_ROI_rect(roi, mask_arr.shape[0], mask_arr)
dynamic_curve = np.zeros(len(acq_dict.keys())-1)
#Use the ROI as a mask to get the mean from each time point
for key in acq_dict:
    if key!=0:
        sorted_slices_list = sort_slices(acq_dict[key], dir_path)
        time_point = pydicom.dcmread(os.path.join(dir_path, sorted_slices_list[sl_no]))
        time_point_arr = time_point.pixel_array
        _,mean,_ = plot_ROI_rect(roi, time_point_arr.shape[0], time_point_arr, plot=False)
        dynamic_curve[int(key)-1] = mean
#Save the mean in an array and plot it
plt.plot(dynamic_curve)
plt.show()

#%%
'''Calculate the parameters per pixel'''
#Do this for every pixel in the ROI
#Store the results in a list with the same dimensions as the flatten roi
#Reshape at the end and plot
sl_no = 37
mask_slices_list = sort_slices(acq_dict[0], dir_path)
mask_sl = pydicom.dcmread(os.path.join(dir_path, mask_slices_list[sl_no]))
mask_arr = mask_sl.pixel_array
flattened_mask = np.ndarray.flatten(mask_arr)
roi = [170, 150, 10, 10]
all_time_points = np.zeros([len(acq_dict.keys())-1, flattened_mask.shape[0]])
me_all = np.zeros([flattened_mask.shape[0]])
ttp_all = np.zeros([flattened_mask.shape[0]])
dynamic_curve = np.zeros(len(acq_dict.keys())-1)

#Get all the time points flattened in the same variable
for key in acq_dict:
    if key!=0:
        sorted_slices_list = sort_slices(acq_dict[key], dir_path)
        time_point = pydicom.dcmread(os.path.join(dir_path, sorted_slices_list[sl_no]))
        time_point_arr = time_point.pixel_array
        flattened_time_point = np.ndarray.flatten(time_point_arr)
        all_time_points[key-1] = flattened_time_point

#for pixel in range(all_time_points.shape[1]):
for pixel in range(25600, 38400):
    dynamic_curve = all_time_points[:, pixel]
    gauss_filt = scp.ndimage.gaussian_filter1d(dynamic_curve, 3)
    t_zero = find_t_zero(gauss_filt)
    plt.plot(dynamic_curve, 'b')
    plt.plot(gauss_filt, 'y')
    plt.plot(t_zero, gauss_filt[t_zero], '*r')
    plt.plot(np.argmax(gauss_filt), np.amax(gauss_filt), '*k')
    plt.show()
    m,me,ttp = parameters(gauss_filt, t_zero)
    me_all[pixel] = me
    ttp_all[pixel] = ttp
    
ttp_all = np.reshape(ttp_all, mask_arr.shape)
plt.imshow(ttp_all)
plt.colorbar()
plt.title('Time to peak') 
plt.show()

#me_all[me_all>20000] = 0
me_all = np.reshape(me_all, mask_arr.shape)
plt.imshow(me_all)
plt.colorbar()
plt.title('Maximum enhancement') 
plt.show()
#%%
'''Apply median filter'''
med_filt = scp.signal.medfilt(dynamic_curve)
gauss_filt = scp.ndimage.gaussian_filter1d(dynamic_curve, 3)
t_zero = find_t_zero(gauss_filt)

result_a = slope_a*x_data_a+intercept_a
result_d = slope_d*x_data_d+intercept_d

plt.plot(dynamic_curve, 'b')
#plt.plot(med_filt, 'g')
plt.plot(gauss_filt, 'y')
plt.plot(t_zero, gauss_filt[t_zero], '*r')
plt.plot(np.argmax(gauss_filt), np.amax(gauss_filt), '*k')
plt.plot(x_data_a, result_a, 'g')
plt.plot(x_data_d, result_d, 'g')
plt.show()
