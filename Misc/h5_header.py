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


path = '/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD016/ScanArchives'
series_list = os.listdir(path)

for s in series_list:
    series_path = os.path.join(path,s)
    archive_list = os.listdir(series_path)
    print('-----------------',str(s),'--------------')
    for scan in archive_list:
        scan_path = os.path.join(series_path, scan)
        f = h5py.File(scan_path, 'r')
        header = f['DownloadMetaData']
        #header = f['OriginalHeader.xml']
        header_content=header[:]
        header_bytes = b''.join(header_content)
        header_string = header_bytes.decode('utf-8')
        result = re.search('SeriesDescription\" : (.*),', header_string)
        #result = re.search('ScanType\>(.*)<', header_string)
        scan_type = result.group(1)
        print(scan_type)
        #series = re.search('SeriesNumber\" : (.*),', header_string)
        #print(series.group(0))
    print('\n')

'''
#Show the header: f.keys()
#Open each of the header's parts: f['part name'][:]

def visitor_func(name, node):
    if isinstance(node, h5py.Group):
        print(node.name, 'is a Group')
    elif isinstance(node, h5py.Dataset):
       if (node.dtype == 'object') :
            print (node.name, 'is an object Dataset')
       else:
            print(node.name, 'is a Dataset')   
    else:
        print(node.name, 'is an unknown type')
        
f.visititems(visitor_func)
'''