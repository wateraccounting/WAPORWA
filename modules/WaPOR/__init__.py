# -*- coding: utf-8 -*-
"""
Authors: Bich Tran
         IHE Delft 2019
Contact: b.tran@un-ihe.org
Repository: https://github.com/wateraccounting/watools
Module: Collect/WaPOR

Description:
This script collects WaPOR data from the WaPOR API. 
The data is available between 2009-01-01 till present.

Example:
from watools.Collect import WaPOR
WaPOR.PCP_monthly(Dir='C:/Temp/', Startdate='2009-02-24', Enddate='2009-03-09',
                     latlim=[50,54], lonlim=[3,7])
WaPOR.AETI_monthly(Dir='C:/Temp/', Startdate='2009-02-24', Enddate='2009-03-09',
                     latlim=[50,54], lonlim=[3,7])
"""
from .PCP_monthly import main as PCP_monthly
from .PCP_yearly import main as PCP_yearly
from .PCP_daily import main as PCP_daily
from .PCP_dekadal import main as PCP_dekadal
from .RET_monthly import main as RET_monthly
from .RET_yearly import main as RET_yearly
from .AET_yearly import main as AET_yearly
from .AET_monthly import main as AET_monthly
from .AET_dekadal import main as AET_dekadal
from .I_yearly import main as I_yearly
from .I_dekadal import main as I_dekadal
from .LCC_yearly import main as LCC_yearly
from .WaporAPI import __WaPOR_API_class

__all__ = ['PCP_monthly','PCP_yearly','PCP_daily','PCP_dekadal',
           'RET_monthly','RET_yearly',
           'AET_monthly','AET_yearly','AET_dekadal',
           'I_yearly','LCC_yearly','I_dekadal']
__doc__ = """module for FAO WAPOR API"""
__version__ = '0.1'

# initiate class for .his-files
API = __WaPOR_API_class()

API.Token=input('Your WaPOR API Token: ')
