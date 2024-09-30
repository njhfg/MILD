#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 13:50:36 2024

@author: cristina
"""

'''DICO STAR dynamic contrast-enhanced acquisition'''

import os
import pydicom
from natsort import natsorted


dir_path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD004/RAW/Disco_Star'
slices = os.listdir(dir_path)
#slices = natsorted(slices) #sort in natural order
slices  = slices[3:4]

for sl in slices:
    sl_path = os.path.join(dir_path, sl)
    data = pydicom.dcmread(sl_path)
    temp_pos = data[0x00200100].value #temporal position identifier
    print(temp_pos)
