# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 09:37:51 2019

@author: ntr002
"""
import datetime
import pickle
import os

def pickle_out(dict_):
    Now=datetime.datetime.now()
    pickle_fh=os.path.join(dict_['Dir'],"Info_%s.pickle"%(Now.strftime("%Y%m%d_%Hh%M")))
    pickle_out = open(pickle_fh,"wb")
    pickle.dump(dict_, pickle_out)
    pickle_out.close()
    return pickle_fh
    
def pickle_in(pickle_fh):
    dict_=dict()
    pickle_in=open(pickle_fh,"rb")
    dict_=pickle.load(pickle_in)
    pickle_in.close()       
    return dict_  