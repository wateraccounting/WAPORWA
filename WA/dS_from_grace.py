# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 11:44:46 2019

@author: ntr002
"""

import pandas as pd

grace_basin_csv=r"D:\FAO\WA_Sheet1\Main\Jordan\data\GRACE\Jordan_v190402.csv"

ts_grace=pd.read_csv(grace_basin_csv,sep=',',index_col=0)