# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 08:50:21 2019

@author: ntr002

Adapted from Bert Coerver and Claire Michailovsky
"""
import os
import datetime

def find_year(fh):
    """
    Finds index of possible year and month in a string if the date is of format 
    yyyymm or yyyy{char}mm for years between 1900 and 2030
    """
    basename = os.path.basename(fh)    
    years = ['{0}'.format(i) for i in range(1900, 2030)]
    options = {}
    i = 0
    for y in years:
        index1 = basename.find(y)
        index = index1 - len(basename)
        if index1 > 0:            
            date=datetime.date(year=int(fh[index:index+4]),month=1,day=1)
            options[i] = (date,[index, index+4])
    if len(options.keys()) == 0:
        print('Could not find datestring')
    elif len(options.keys()) > 1:
        print('Multiple possible locations for datestring')    
    return options[0]

def find_month(fh):
    """
    Finds index of possible year and month in a string if the date is of format 
    yyyymm or yyyy{char}mm for years between 1900 and 2030
    """
    basename = os.path.basename(fh)
    months =['{0:02d}'.format(i) for i in range(1,13)]    
    _,[index,_]=find_year(fh)    
    if basename[index+4:index+6] in months:                
        date=datetime.datetime.strptime(fh[index:index+6], '%Y%m').date()               
        options = (date,[index, index+4], [index+4, index+6])    
    elif basename[index+5:index+7] in months:
        date_str='%s%s'%(fh[index:index+4],fh[index+5:index+7])
        date=datetime.datetime.strptime(date_str, '%Y%m').date()  
        options = (date,[index, index+4], [index+5, index+7])  
    return options
        
def find_date(fh):
    """
    Finds index of possible year and month in a string if the date is of format 
    yyyymmdd or yyyy{char}mm{char}dd for years between 1900 and 2030
    """
    basename = os.path.basename(fh)
    days=['{0:02d}'.format(i) for i in range(1,32)]
    date,[iyear,_],[imonth,_]=find_month(fh) 
    if basename[imonth+2:imonth+4] in days:
        date=datetime.date(date.year,date.month,int(basename[imonth+2:imonth+4]))            
        options = (date,[iyear, iyear+4], [imonth, imonth+2],[imonth+2, imonth+4])
    if basename[imonth+3:imonth+5] in days:
        date=datetime.date(date.year,date.month,int(basename[imonth+3:imonth+5]))            
        options = (date,[iyear, iyear+4], [imonth, imonth+2],[imonth+3, imonth+5]) 
    return options