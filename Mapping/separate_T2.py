#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 09:21:03 2024

@author: cristina
"""

'''Separate the series in the Propelelr acquisition based on the TE'''

import os
import pydicom

dir_path = r'/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15619/Propeller_BW62.5'
slices_list = os.listdir(dir_path)

for sl in slices_list:
    sl_path = os.path.join(dir_path, sl)
    s = pydicom.dcmread(sl_path)
    te = float(s[0x00180081].value) #echo time
    if te==10.336:
        s.save_as(os.path.join('/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15619/Propeller_BW62.5_separated/TE10',sl))
    elif te==51.68:
        s.save_as(os.path.join('/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15619/Propeller_BW62.5_separated/TE50',sl))
   