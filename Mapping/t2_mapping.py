#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 10:00:42 2024

@author: cristina
"""

'''T2 mapping script'''

#%% 'Imports'

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
main_dir = '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam14954/T2_map'
dir_paths = os.listdir(main_dir)
no_dirs = len(dir_paths)

for i in range(no_dirs):
    dir_paths[i] = os.path.join(main_dir, dir_paths[i])

te = [10, 50] 
#te = [10,20,30,40,50,60,70,80,90,100]
#%%

def function_linear(te,t2):
    #because it's logarithmic
    signal = t2*te
    return signal

def function_exponential(te, t2):
    signal = np.exp(np.negative(te)/t2)
    return signal

def sort_slices (slices_list, dir_path):
    '''Sort slices according to the instance numebr tag'''
    pos = []
    for sl in slices_list:
        img = pydicom.dcmread(os.path.join(dir_path, sl), force=True) #read the current slice
        pos.append(img[0x00200013].value) #save the original order of instance number
        
    sort_args = np.argsort(pos) #sort the instance numbers and save the new order of the list arguments
    slices_list[:] = [slices_list[i] for i in sort_args] #save the reordered slices names based on the instance numbers
        
    return slices_list


def plot_ROI(xc, yc, r, im_size, im):
    """
    Overlays a red circle over an image and returns the mean of the ROI
    
    Inputs
    ---------
    xc: x coordinate of the center of the circle (298/251/205/159)
    yc: y coordinate of the center of the circle (248)
    r: cirlce radius
    im_size: the size of the image
    im: the image to show
    
    Returns
    -------
    plot
    mean_ROI: the mean of the circular ROI

    """
    circle = plt.Circle((xc, yc), r, color='r')
    fig, ax = plt.subplots() 
    ax.imshow(im)
    ax.add_patch(circle)
    
    x, y = np.ogrid[:im_size, :im_size]
    mask = np.zeros((im_size, im_size))
    mask[(x-xc)**2 + (y-yc)**2 < r**2] = 1
    print('ROI mean', np.mean(im[mask==1]))
    return np.mean(im[mask==1])

def plot_ROI_rect(roi, im_size, im):
    """
    Overlays a red circle over an image and returns the mean of the ROI
    
    Inputs
    ---------
    xc: x coordinate of the center of the circle (298/251/205/159)
    yc: y coordinate of the center of the circle (248)
    r: cirlce radius
    im_size: the size of the image
    im: the image to show
    
    Returns
    -------
    plot
    mean_ROI: the mean of the circular ROI

    """
    rect = Rectangle((roi[0], roi[1]), roi[2], roi[3], color='r')
    fig, ax = plt.subplots() 
    ax.imshow(im)
    ax.add_patch(rect)
    
    mask = np.zeros((im_size, im_size))
    mask[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]] = 1
    print('ROI mean', np.mean(im[mask==1]))
    area = np.count_nonzero(mask)
    return mask, np.mean(im[mask==1]), area


def select_ROI(xc, yc, r, im_size):
    """
    Overlays a red circle over an image and returns the mean of the ROI
    
    Inputs
    ---------
    xc: x coordinate of the center of the circle (298/251/205/159)
    yc: y coordinate of the center of the circle (248)
    r: cirlce radius
    im_size: the size of the image
    im: the image to show
    
    Returns
    -------
    plot
    mean_ROI: the mean of the circular ROI

    """    
    x, y = np.ogrid[:im_size, :im_size]
    mask = np.zeros((im_size, im_size))
    mask[(x-xc)**2 + (y-yc)**2 < r**2] = 1
    area = np.count_nonzero(mask)
    return mask, area
    
    
#%%
'''Fit with the log of the signal over a linear function'''

no_slices = len(os.listdir(os.path.join(main_dir, dir_paths[0])))

slices_matrix = [] #each row is a folder containing the ordered list of slices names
#Create a list of the sorted slices names (based on instance number) for each directory
for i,d in enumerate(dir_paths):
    curr_dir_path = os.path.join(main_dir, d)
    slices_list = os.listdir(d)
    slices_matrix.append(sort_slices(slices_list, d))
'''Getting the ROI for one slice'''
slice_no = 35
slices_list = slices_matrix[0] #the slices names list of the first folder
slice_path = os.path.join(dir_paths[0], slices_list[slice_no]) #path of the current slice
s = pydicom.dcmread(slice_path) #read the DICOM data
s_arr = s.pixel_array #get the array
roi = cv2.selectROI(s_arr)
mask,_, area = plot_ROI_rect(roi, 512, s_arr)
data_matrix = np.zeros((no_dirs, area)) 
decay_matrix = np.zeros(no_dirs) 
t2_est = np.zeros((area)) #empty T2 map  

'''Mapping for the selected ROI'''
for j in range(no_dirs):   
    #keep the signal intensities values in a matrix of number of folders x number of pixels per slice
    slices_list = slices_matrix[j] #the slices names list of the current folder
    slice_path = os.path.join(dir_paths[j], slices_list[slice_no]) #path of the current slice
    s = pydicom.dcmread(slice_path) #read the DICOM data
    s_arr = s.pixel_array #get the array
    _,decay_matrix[j],_ = plot_ROI_rect(roi, 512, s_arr)
    s_arr = s_arr[mask==1] #selct only the ROI from the array
    print('Maximum array value', np.amax(s_arr))
    s_arr = s_arr.flatten()
    data_matrix[j,:] = s_arr #add the flat array to the data matrix
for t in range(data_matrix.shape[1]): #number of pixels
    #do the curve fitting for each pixel location
    try:
        params, _ = curve_fit(function_linear, te, np.log(data_matrix[:, t]))
        t2_est[t] = 1/params[0] #because the slope is 1/T2
        #t2_est[t] = params[0]
    except:
        pass
t2_est[t2_est==np.inf]=0
t2_est[t2_est>100]=0
t2_est = t2_est.reshape((roi[3], roi[2]))
t2_max = np.amax(t2_est)

#Histogram equalization
t2_eq = exposure.equalize_hist(t2_est)
t2_eq = t2_eq*t2_max
t2_eq = t2_eq.astype(np.float32)
fig = plt.figure()
im = plt.imshow(t2_eq, cmap='plasma', vmin=np.amin(t2_eq), vmax=t2_max)
fig.colorbar(im)

plt.figure()
plt.plot(te, decay_matrix)
plt.title("Signal decay")


''' Mapping for the whole image
for i in range(no_slices):
    decay_matrix = np.zeros(no_dirs) 
    data_matrix = np.zeros((no_dirs, 512*512)) #TO DO: change the hard coded values
    t2_est = np.zeros((512*512)) #empty T2 map
    for j in range(no_dirs):   
        #keep the signal intensities values in a matrix of number of folders x number of pixels per slice
        slices_list = slices_matrix[j] #the slices names list of the current folder
        slice_path = os.path.join(dir_paths[j], slices_list[i]) #path of the current slice
        s = pydicom.dcmread(slice_path) #read the DICOM data
        s_arr = s.pixel_array #get the array
        print('Maximum array value', np.amax(s_arr))
        decay_matrix[j] = plot_ROI(xc=200, yc=257, r=6,im_size=512, im=s_arr)
        s_arr = s_arr.flatten()
        data_matrix[j,:] = s_arr #add the flat array to the data matrix
    for t in range(data_matrix.shape[1]): #number of pixels
        #do the curve fitting for each pixel location
        try:
            params, _ = curve_fit(function_linear, te, np.log(data_matrix[:, t]))
            t2_est[t] = 1/params[0] #because the slope is 1/T2
            #t2_est[t] = params[0]
        except:
            pass
    t2_est[t2_est==np.inf]=0
    t2_est[t2_est>100]=0
    t2_est = t2_est.reshape((512, 512))
    t2_max = np.amax(t2_est)
    
    #Histogram equalization
    t2_eq = exposure.equalize_hist(t2_est)
    t2_eq = t2_eq*t2_max
    t2_eq = t2_eq.astype(np.float32)
    fig = plt.figure()
    im = plt.imshow(t2_eq, cmap='plasma', vmin=np.amin(t2_eq), vmax=t2_max)
    fig.colorbar(im)
    
    plt.figure()
    plt.plot(te, decay_matrix)
    plt.title("Signal decay")
    '''

    

    #im = Image.fromarray(t2_eq)
    #im.save('/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam_phantom_Ieva/t2map/'+str(i)+'.tif', format='TIFF')
    

#%%
'''Fit with the signal over the exponential function'''
dir_paths = ['/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam_phantom_Ieva/TE10', 
             '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam_phantom_Ieva/TE50',
             '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam_phantom_Ieva/TE80',
             '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam_phantom_Ieva/TE100']

no_slices = len(os.listdir(dir_paths[0]))
no_dirs = len(dir_paths)
te = [10,50, 80, 100] #to try: use exact values from the DICOM tags

slices_matrix = [] #each row is a folder containing the ordered list of slices names
#Create a list of the sorted slices names (based on instance number) for each directory
for i,d in enumerate(dir_paths):
    slices_list = os.listdir(d)
    slices_matrix.append(sort_slices(slices_list, d))


for i in range(no_slices):
    mask, area = select_ROI(206, 267, 6, 512)
    data_matrix = np.zeros((no_dirs, area)) 
    for j in range(no_dirs):   
        #keep the signal intensities values in a matrix of number of folders x number of pixels per slice
        slices_list = slices_matrix[j] #the slices names list of the current folder
        slice_path = os.path.join(dir_paths[j], slices_list[i]) #path of the current slice
        s = pydicom.dcmread(slice_path) #read the DICOM data
        s_arr = s.pixel_array #get the array        
        s_arr = s_arr[mask==1]     
        s_arr = s_arr.flatten()
        data_matrix[j,:] = s_arr #add the flat array to the data matrix
    for t in range(data_matrix.shape[1]): #number of pixels
        #do the curve fitting for each pixel location
        try:
            params, _ = curve_fit(function_exponential, te, data_matrix[:, t])
            t2_est[t] = 1/params[0] #because the slope is 1/T2
            #t2_est[t] = params[0]
        except:
            pass
    t2_est[t2_est==np.inf]=0
    t2_est[t2_est>100]=0
    #t2_est_exp = t2_est.reshape((512, 512))
    #t2_max = np.amax(t2_est)
    
    #Histogram equalization
    t2_eq = exposure.equalize_hist(t2_est)
    t2_eq = t2_eq*t2_max
    t2_eq = t2_eq.astype(np.float32)
    fig = plt.figure()
    im = plt.imshow(t2_eq, cmap='plasma', vmin=np.amin(t2_eq), vmax=t2_max)
    fig.colorbar(im)
    
    #mean_sphere = plot_ROI(xc=298, yc=248, r=2,im_size=512, im=t2_eq)  #xc=298/251/205/159
    
    plot_ROI(xc=298, yc=267, r=2,im_size=512, im=t2_eq)
    plot_ROI(xc=206, yc=267, r=2,im_size=512, im=t2_eq)
    
    im = Image.fromarray(t2_eq)
    im.save('/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam_phantom_Ieva/t2map/'+str(i)+'.tif', format='TIFF')
    
    #plt.savefig('/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15093/propeller_t2map/'+str(i)+'.jpeg')    

#%% 
"Plot the decay"

dir_paths = ['/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam_phantom_Ieva/TE10', 
             '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam_phantom_Ieva/TE50',
             '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam_phantom_Ieva/TE80',
             '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam_phantom_Ieva/TE100']

no_slices = len(os.listdir(dir_paths[0]))
no_dirs = len(dir_paths)
#te = [36.258, 49.699, 82.079]
te = [10,50, 80, 100]

#Save the names of the sorted slices for all directories
slices_matrix = []
for i,d in enumerate(dir_paths):
    slices_list = os.listdir(d)
    slices_matrix.append(sort_slices(slices_list, d))


data_matrix = np.zeros(no_dirs) 
for j in range(no_dirs):   
    sl = slices_matrix[j][30] #get a specific slice name 
    slice_path = os.path.join(dir_paths[j], sl) 
    s = pydicom.dcmread(slice_path)
    s_arr = s.pixel_array
    
    data_matrix[j] = plot_ROI(xc=206, yc=267, r=6,im_size=512, im=s_arr)
plt.figure()
plt.plot(te, data_matrix)
plt.title("Signal decay")

plt.figure()
plt.plot(te, np.log(data_matrix))
plt.title("Log signal decay")
#%% 'SSFSE separation'

dir_path = r'/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15338/dda25/s515'
slices_list = os.listdir(dir_path)

for sl in slices_list:
    sl_path = os.path.join(dir_path, sl)
    s = pydicom.dcmread(sl_path)
    te = s[0x00180081].value #echo time
    if te=='5':
        s.save_as(os.path.join('/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15338/dda25/TE5',sl))
    elif te=='10':
        s.save_as(os.path.join('/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15338/dda25/TE10',sl))
    elif te=='20':
        s.save_as(os.path.join('/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15338/dda25/TE20',sl))
    else:
        s.save_as(os.path.join('/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15338/dda25/TE40',sl))

