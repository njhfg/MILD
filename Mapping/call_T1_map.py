#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 14:33:05 2024

@author: cristina
"""

'''Call T1 mapping'''

#Call T1 mapping for each of the time points of contrast injection (0, 1,5,10?)
import sys
import os
from natsort import natsorted
sys.path.append('/media/data/cristina_data/scripts')
import T1_map
import matplotlib.pyplot as plt

main_dir = r'/home/cristina/mrpg_share2/Cristina/Patient_scans/MILD003/RAW/T1_mapping'
dir_paths = os.listdir(main_dir)
dir_paths = natsorted(dir_paths) #sort in natural order (0,1,5,10 min)
no_dirs = len(dir_paths)

for i in range(no_dirs):
    #get the paths of the subfolders corresponding to each flip angle
    dir_paths[i] = os.path.join(main_dir, dir_paths[i])

t1 = []

for d in dir_paths:
    t1.append(T1_map.main(d))
    print('Finished ', d)
    
plt.figure()
colors_list = ['b', 'g', 'r', 'k']
labels_list = ['pre', '1 min', '5 min', '10 min']
for i in range(no_dirs):
    curr_t1 = t1[i]
    plt.plot(curr_t1[0:50], colors_list[i], label = labels_list[i])
    plt.show()
plt.legend()