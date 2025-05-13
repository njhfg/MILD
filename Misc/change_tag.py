#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 13:44:07 2025

@author: cristina
"""

'''Change the description tag for the DL data'''


'''Right now the series number for the multi-phase recon is OriginalSeriesNumber*100.
We could differenciate DL_ZTE, PhaseBinning (1 phase, 2 phases or more), and WASPI_gated/ungated: 

(DL_ZTE+WaspiGated/Ungated)*1000+OriginalSeriesNumber*100+NumberOfPhases
DL_ZTE can be 0-100, usually 75, while WASPIGated/Ungated could be just a binary number 0/1)
'''
#TODO: change the hard

import pydicom
import os

root_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD010/Processed/GE/Exam16493/Series20/PhaseBinning/Phases16/WASPIGated/CSC/DL75/DICOM'

#Create the new description from the names of the directories in the path
name_parts = root_path.split('/')

#DL level
dl = name_parts[-2][-2:]
if len(dl)!=2:
    dl = '0'+dl

#WASPI gating
if 'n' in name_parts[-4]:
    waspi = '0' #ungated
else:
    waspi = '1' #gated

#Original series number
series = name_parts[-7][-2:]
if len(series)!=2:
    series = '0'+series
    
phases = '16'

new_desc = name_parts[-4]+' '+name_parts[-3]+' '+name_parts[-2]
new_series = dl+waspi+series+phases

files_list = os.listdir(root_path)

for f in files_list:
    file_path = os.path.join(root_path, f)
    ds = pydicom.dcmread(file_path)
    old_desc = ds[0x0008103E] #description tag
    old_desc.value = new_desc
    old_series = ds[0x00200011] #old series number
    old_series.value = new_series
    ds.save_as(file_path)
    
    

