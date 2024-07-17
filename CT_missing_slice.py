# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 16:19:30 2022

@author: 085220

Script to find the missing slice in a DICOM scan by checking the differences between the slices' positions.
If one difference is not equal to the rest then there is a slice missing there. 
The script also corrects the missing slice by changing the tags of the slices after the gap.
"""
import pydicom
import numpy as np
import os
import pandas as pd

def sort_slices (slices):
    '''Sort slices according to the Instance number tag'''
    pos = []
    for sl in slices:
        img = pydicom.dcmread(os.path.join(input_dir_path, sl), force=True) #read the current slice 
        pos.append(img[0x00200013].value) #save the original order of instance numbers
    
    sort_args = np.argsort(pos) #sort the instance numbers
    slices[:] = [slices[i] for i in sort_args] #reorder the slices according to the ascending order of instance numbers
    
    return slices #the reordered slices

def sl_loc_img_pos(slices):
    '''Make the slice location the same as the alst value of the image position'''
    for sl in slices:
        img = pydicom.dcmread(os.path.join(input_dir_path, sl), force=True) #read the current slice 
        img_pos = img[0x00200032].value #image position tag
        img[0x00201041].value = img_pos[-1] #replace the slice location with teh last value of image position
        img.save_as(os.path.join(input_dir_path, sl))

def find_locations (slices):
    '''Find all the missing slices' locations based on the Slice Location tag
    Where the difference between the slice locations is not the same as the rest,
    there should be a slice missing. This function returns all locations of missing slices. '''
    locations = []
    list_missing_slices = []
    increments = []
    loc = []
    for sl in slices:
        img = pydicom.dcmread(os.path.join(input_dir_path, sl))
        loc.append(img[0x00201041].value) #save all the slice location values
    dif = np.diff(loc) #take the derivative of the loc (take the difference between each element and the one before it)
    dif = np.around(dif, decimals=1)
    uniq = np.unique(dif) #find how many unique differences resulted
    if len(uniq) == 1: #if all the subtractions gave the same result, then there is no slice missing
        return -1
    else: #if there are more difference values
        uniq = abs(uniq) 
        uniq = np.sort(uniq) #sort the difference values
        for i in range(1, len(uniq)):
            #the first value in uniq is the normal difference in slice location
            increment = uniq[i] 
            missing_slices = abs(increment)/abs(uniq[0])-1 #number of missing slices
            location, = np.where(abs(dif)==increment) #find the location where the difference is the abnormal one
            increment = increment - uniq[0]
            for l in location:
                l = l+2
                locations.append(l)
                increments.append(increment)
                list_missing_slices.append(missing_slices)
        return locations, increments, list_missing_slices

def find_missing (slices):
    '''Find the missing slices' locations based on the Slice Location tag
    Where the difference between the slice locations is not the same as the rest,
    there should be a slice missing. This function returns only when there is only one location of the missing slices'''
    locations = []
    loc = []
    for sl in slices:
        img = pydicom.dcmread(os.path.join(input_dir_path, sl))
        loc.append(img[0x00201041].value) #save all the slice location values
    dif = np.diff(loc) #take the derivative of the loc (take the difference between each element and the one before it)
    dif = np.around(dif, decimals=1)
    if dif[0]>0:
        positive = True
    else:
        positive = False
    uniq = np.unique(dif) #find how many unique differences resulted
    if len(uniq) == 1: #if all the subtractions gave the same result, then there is no slice missing
        return -1
    else: #if there are more difference values
        uniq = abs(uniq) 
        uniq = np.sort(uniq) #sort the difference values
        #take the second difference value
        #this is done for a case where there is only one slice missing or
        #there is only one value for the abnormal distance
        increment = uniq[1] 
        missing_slices = abs(increment)/abs(uniq[0])-1 #number of missing slices
        location, = np.where(abs(dif)==increment) #find the location where the difference is the abnormal one
        increment = increment - uniq[0]
    return location, increment, missing_slices, len(uniq), positive #the first location where there is a missing slice

def modify_slices (slices, input_dir_path, increment, missing_slices, positive):
    '''Modifiy all the slices' location and instance number tags to account for the missing ones
    The number used to modify them depends on the scan'''
    for sl in slices:
        img = pydicom.dcmread(os.path.join(input_dir_path, sl))
        sl_loc = img[0x00201041] #slice location
        if positive:
            sl_loc.value = sl_loc.value - increment
        else:
            sl_loc.value = sl_loc.value + increment
        im_pos = img[0x00200032] #image position
        '''
        if np.logical_and(im_pos.value[0]<0, sl_loc.value>0):
            im_pos.value[-1] = -sl_loc.value
        else:
            im_pos.value[-1] = sl_loc.value
        '''
        if np.sign(im_pos.value[-1])==np.sign(sl_loc.value):
            im_pos.value[-1] = sl_loc.value
        else:
            im_pos.value[-1] = -sl_loc.value
        instance_no = img[0x00200013] #instance number
        instance_no.value = str(int(instance_no.value)-int(missing_slices))
        img.save_as(os.path.join(input_dir_path, sl), write_like_original=False) #replace the original image with the one with modified tags
        
def remove_tags (slices):
    '''Remove the tags that do not appear in all the slices from the same scan'''
    for sl in slices:
        img = pydicom.dcmread(os.path.join(input_dir_path, sl))
        if 'PerformedProcedureStepStartDate' in img:
            del img.PerformedProcedureStepStartDate
            del img.PerformedProcedureStepStartTime
            img.save_as(os.path.join(input_dir_path, sl), write_like_original=False)
            
def save_slices(slices, input_dir, output_dir):
    for sl in slices: 
        img = pydicom.dcmread(os.path.join(input_dir, sl))
        img.save_as(os.path.join(output_dir, sl), write_like_original=True)
#%%
'''Check if the tags are consistent for all the slices and delete the extra ones'''

#TODO: Automate the removal of extra slices 
    
DICOM_path = r'D:\Cristina\Data_job\Erasmus\Baseline' #parent directory path
dirs = os.listdir(DICOM_path) #list of the directories in the parent one (each one is a scan)
for directory in dirs:
    print("processing dir: ", directory)
    input_dir_path = os.path.join(DICOM_path, directory) #current directory path
    slices = os.listdir(input_dir_path)
    dicts = []
    for sl in slices:
        img = pydicom.dcmread(os.path.join(input_dir_path, sl))
        dicts.append(img.dir())
    u = np.unique(dicts) #to check if the tags are consistent across the slices
    u1 = u[0]
    u2 = u[1]
    ls = list(set(u1)-set(u2))

    #remove_tags(slices)

#%%
'''Modify the scans' slice location and instance number tags'''

DICOM_path = r'D:\082_ASPEN_SubStudy_CT_Batch1_MissingSlices\082_096\082_096' #parent directory path
#output_dir = r'D:\Cristina\Data_job\RECOVER_output'
dirs = os.listdir(DICOM_path) #list of the directories in the parent one (each one is a scan)
#dirs = dirs[3:4] #select only some scans from the folder
#TODO: select only the dirs taht have DICOM and print the summary of the possible missing slices
for directory in dirs:
    input_dir_path = os.path.join(DICOM_path, directory) #current directory path
    #out_dir_name = directory+'_tags'
    #out_dir_path = os.path.join(output_dir, out_dir_name)
    slices = os.listdir(input_dir_path)
    sorted_slices = np.copy(slices)
    sorted_slices = sort_slices(slices)
    #sl_loc_img_pos(slices)
    #remove_tags(sorted_slices)
    
    if find_missing(sorted_slices) != -1: #if there are missing slices
        location, increment, missing_slices, unique, positive = find_missing (sorted_slices) #the location of the missing slice in the scan
        if unique>2 or len(location)>1: #if there are multiple differences or locations of missing slices don't do anything
            print('Not processed: ', directory)
            #continue
        else:
            print('Processed: ', directory)
            location = location[0]+1
            #locations.append(location)
            #if os.path.exists(out_dir_path) == False:
                #os.mkdir(out_dir_path)
            #slices_to_save = sorted_slices[:location]
            #save_slices(slices_to_save, input_dir_path, out_dir_path)
            slices_to_modify = sorted_slices[location:]
            modify_slices(slices_to_modify, input_dir_path, increment, missing_slices, positive)
    else:
        print('No missing slices: ', directory)
        
#%%
'''Add the slices missing by copying the slces around the missing ones'''

DICOM_path = r'D:\Cristina\Data_job\RECOVER_unable_to_analyze' #parent directory path
dirs = os.listdir(DICOM_path) #list of the directories in the parent one (each one is a scan)
dirs = dirs[2:3] #select only some scans from the folder
locations = []
dicts = []
for directory in dirs:
    dir_path = os.path.join(DICOM_path, directory) #current directory path
    slices = os.listdir(dir_path)
    sorted_slices = np.copy(slices)
    sorted_slices = sort_slices(slices)
    
    if find_missing (sorted_slices) != -1: #if there are missing slices
        location = find_missing (sorted_slices)+1 #the location of the missing slice in the scan
        location = location[0]
        slices_to_modify = sorted_slices[location:]

        sl1_path = os.path.join(dir_path, slices[location-1])
        sl1 = pydicom.dcmread(sl1_path)
        instance_no1 = sl1[0x00200013]
        instance_no1.value = str(int(instance_no1.value)+1)
        position1 = sl1[0x00201041]
        position1.value = str(float(position1.value)-0.5)
        im_pos1 = sl1[0x00200032] #image position
        im_pos1.value[-1] = position1.value
        sl1.save_as(os.path.join(dir_path, 'slice1'), write_like_original=False)
    
        sl2_path = os.path.join(dir_path, slices[location])
        sl2 = pydicom.dcmread(sl2_path)
        instance_no2 = sl2[0x00200013]
        instance_no2.value = str(int(instance_no2.value)-1)
        position2 = sl2[0x00201041]
        position2.value = str(float(position2.value)+0.5)
        im_pos2 = sl2[0x00200032] #image position
        im_pos2.value[-1] = position2.value
        sl2.save_as(os.path.join(dir_path, 'slice2'), write_like_original=False)

#%%
'''Print the values of a certain tag across all the scans'''

'''
Manufacturer's model name (0008, 1090)
Software versions (0018, 1020)
Convolution kernel (0018, 1210)
'''

DICOM_path = r'D:\Cristina\Data_job\RECOVER_unable_to_analyze\All_scans' #parent directory path
dirs = os.listdir(DICOM_path) #list of the directories in the parent one (each one is a scan)
tag_list = []
for directory in dirs:
    input_dir_path = os.path.join(DICOM_path, directory) #current directory path
    slices = os.listdir(input_dir_path)
    slice_path = slices[0]
    full_slice_path = os.path.join(input_dir_path, slice_path)
    img = pydicom.dcmread(full_slice_path)
    scanner = img[0x00181210].value 
    tag_list.append(scanner) 
    
unique_tags = np.unique(tag_list)

#%%
'''Save the gaps values in an Excel file'''

DICOM_path = r'G:\RECOVER_unable_to_analyze' #parent directory path
excel_path = r"D:\Cristina\Data_job\RECOVER_unable_to_analyze\2022_12_01_RECOVER_failed_scan_IDs_v2.xlsx"
excel = pd.read_excel(excel_path)
dirs = os.listdir(DICOM_path) #list of the directories in the parent one (each one is a scan)
pat_ids = []
for directory in dirs:
    pat_id = directory.split('_')
    pat_id = pat_id[0]+'_'+pat_id[1]
    input_dir_path = os.path.join(DICOM_path, directory) #current directory path
    slices = os.listdir(input_dir_path)
    sorted_slices = np.copy(slices)
    sorted_slices = sort_slices(slices)
    if find_locations (sorted_slices) != -1:
        location, increments, list_missing_slices = find_locations(sorted_slices)
        print(location)
        for index, row in excel.iterrows(): #iterate through the rows of the keylist  
            if row['LA CT nr'] == pat_id: 
                if pat_id in pat_ids:
                    new_row = excel.loc[index]
                    excel = excel.append(new_row, ignore_index=True)
                    excel.loc[len(excel)-1,'Gaps'] = str(location)
                    excel.loc[len(excel)-1,'Reconstruction'] = directory
                    excel.loc[len(excel)-1,'Unnamed: 0'] = len(excel)-1
                    pat_ids.append(pat_id)
                else:
                    excel.loc[index,'Gaps'] = str(location)
                    excel.loc[index,'Reconstruction'] = directory
                    pat_ids.append(pat_id)
    else:
        for index, row in excel.iterrows(): #iterate through the rows of the keylist
            if row['LA CT nr'] == pat_id:
                if pat_id in pat_ids:
                    new_row = excel.loc[index]
                    excel = excel.append(new_row, ignore_index=True)
                    excel.loc[len(excel)-1,'Gaps'] = '-'
                    excel.loc[len(excel)-1,'Reconstruction'] = directory
                    excel.loc[len(excel)-1,'Unnamed: 0'] = len(excel)-1
                    pat_ids.append(pat_id)
                else:
                    excel.loc[index,'Gaps'] = '-'
                    excel.loc[index,'Reconstruction'] = directory
                    pat_ids.append(pat_id)
                
excel.to_excel(excel_path)