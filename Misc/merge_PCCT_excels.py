# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 13:48:53 2024

@author: 085220
"""

'''
Script that takes as input a folder with Excel files. Each files contains 3 columns with numbers from 1 to 9 or inconclusive. 
The goal is to combine all these files into 1 containing the most chosen option in each cell.
'''

import os
import pandas as pd
import numpy as np
from collections import Counter

def most_frequent(arr):
    occurence_count = Counter(arr) #count how many times each element appears in the array
    freq = occurence_count.most_common(12) #all the elements in order of appearance and how often they appear (list form)
    if freq[0][1]>freq[1][1]: #if the first element appears more times than the second
        return freq[0][0] #then it is the most frequent one
    else: #it means some elements appear an equal number of times
        freq_occurence = [el[1] for el in freq] #save only the number of appearances
        eq_frequent = freq_occurence.count(max(freq_occurence)) #take the maximum number of appearances and count how many times it appears
        return [el[0] for el in freq[0:eq_frequent]] #use this to return the grid numbers that appear that amount of equal times 


main_dir = r'\\cifs.research.erasmusmc.nl\mrpg0002\Cristina\PCCT_score\received'
list_excel_files = os.listdir(main_dir) 

slide_array = np.linspace(1, 72, 72, dtype=int)
result = pd.DataFrame({'Slide':slide_array})
result['First selected image'] = [np.zeros(11, dtype=int) for _ in range(len(result))] #initialize the result table with empty arrays
result['Second selected image'] = [np.zeros(11, dtype=int) for _ in range(len(result))]
result['Third selected image'] = [np.zeros(11, dtype=int) for _ in range(len(result))]

for j in range(len(list_excel_files)): #for each excel file in the list
    path = os.path.join(main_dir, list_excel_files[j])
    excel_file = pd.read_excel(path, usecols=['First selected image', 'Second selected image', 'Third selected image'])
    excel_file.fillna(0, inplace=True) #replace None with 0
    for i, row in result.iterrows(): 
		#replace the string 'none' with 0
        if excel_file.loc[i, 'First selected image']=='none ':
            excel_file.loc[i, 'First selected image'] = 0
        if excel_file.loc[i, 'Second selected image']=='none ':
            excel_file.loc[i, 'Second selected image'] = 0
        if excel_file.loc[i, 'Third selected image']=='none ':
            excel_file.loc[i, 'Third selected image'] = 0
        row['First selected image'][j] = int(excel_file.loc[i, 'First selected image']) #add in result the value from the current file
        row['Second selected image'][j] = int(excel_file.loc[i, 'Second selected image'])
        row['Third selected image'][j] = int(excel_file.loc[i, 'Third selected image'])

output = pd.DataFrame({'Slide':slide_array})   
output['First selected image'] = [ [] for _ in range(len(result))] #initialize the output table with empty lists
output['Second selected image'] = [ [] for _ in range(len(result))]
output['Third selected image'] = [ [] for _ in range(len(result))]
for i in range(72):
	#populate the lists with the result of choosing the most frequent value/s
    output.at[i, 'First selected image'] = most_frequent(result.at[i, 'First selected image'])
    output.at[i, 'Second selected image'] = most_frequent(result.at[i, 'Second selected image'])
    output.at[i, 'Third selected image'] = most_frequent(result.at[i, 'Third selected image'])