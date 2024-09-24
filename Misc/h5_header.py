#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 14:41:42 2024

@author: cristina
"""

import h5py
import os
import xml.etree.ElementTree as ET
import re


path = '/home/cristina/mrpg_share2/Cristina/Volunteer_scans/Exam15188/Series'
series_list = os.listdir(path)

for s in series_list:
    series_path = os.path.join(path,s)
    archive_list = os.listdir(series_path)
    print('-----------------',str(s),'--------------')
    for scan in archive_list:
        scan_path = os.path.join(series_path, scan)
        f = h5py.File(scan_path, 'r')
        header = f['DownloadMetaData']
        header_content=header[:]
        header_bytes = b''.join(header_content)
        header_string = header_bytes.decode('utf-8')
        result = re.search('SeriesDescription\" : (.*),', header_string)
        scan_type = result.group(1)
        print(scan_type)
    print('\n')
