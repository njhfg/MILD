#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 12:29:40 2024

@author: cristina
"""

'''PCCT results Thirona Excel->plots'''

def read_xlsx(path, sheet_name, cols):
    out = pd.read_excel(path, sheet_name=sheet_name, usecols=cols)
    return out

import pandas as pd

parenchyma_path = '/home/cristina/mrpg_share2/Cristina/PCCT_score/Thirona/parenchyma_004_005 - modified.xlsx'
abnormal_path = '/home/cristina/mrpg_share2/Cristina/PCCT_score/Thirona/interstitial_abnormalities_004_005 - modified.xlsx'
parenchyma = pd.read_excel(parenchyma_path, sheet_name='Total lungs 005 - 1000', usecols=['volume', 'recon'])
abnormal = pd.read_excel(abnormal_path, sheet_name='Total lungs 005', usecols=['Interstitial Abnormalities (ml)', 'recon'])


#Group by the recon column
grouped = parenchyma.groupby('recon', as_index=False)['volume'].sum()

#Merge the total volume and abnormalities
total_lungs = pd.merge(grouped, abnormal, how='left', on='recon')

total_lungs.to_excel('/home/cristina/mrpg_share2/Cristina/PCCT_score/Thirona/total_lungs5-1000.xlsx')
