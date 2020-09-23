# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 13:42:44 2019

@author: ntr002
WAPOR LCC to LUWA
"""
#os.chdir(r'D:\FAO\WA_Sheet1\WAPORWA')

from WaPOR import GIS_functions as gis
import numpy as np
import os
from WA.rasterize_shapefile import Rasterize_shapefile

#%% Get reclassification lookup table
#import WaPOR
#WaPOR.API.version=2
#catalog=WaPOR.API.getCatalog()
#cube_info=WaPOR.API.getCubeInfo('L1_LCC_A')
#L1_v2_classes=cube_info['measure']['classes']
#cube_info=WaPOR.API.getCubeInfo('L2_LCC_A')
#L2_v2_classes=cube_info['measure']['classes']

#LCC_LUWA_dict={
#                'PLU':(1,[]),
#               'ULU':(2,[]),
#               'MLU':(3,[41,42]),#Rainfed crop
#               'MWU':(4,[42,50]), #irrigated crop and built-up
#               }
#def _escape_str_paths(*args):
#    outputs=[]
#    for arg in args:
#        new=arg.replace("\\","/")
#        outputs.append(new)
#    return outputs

def Rasterize_shape_basin(shapefile,raster_template,output_raster):
#    shapefile,raster_template,output_raster=_escape_str_paths(shapefile,raster_template,output_raster)
    # driver,NDV,xsize,ysize,GeoT,Projection=gis.GetGeoInfo(raster_template)
    # latlim=[GeoT[3]+ysize*GeoT[5],GeoT[3]]
    # lonlim=[GeoT[0],GeoT[0]+xsize*GeoT[1]]
    # xRes=GeoT[1]
    # yRes=-GeoT[5]
    # Rasterize_shapefile(shapefile,output_raster,latlim,lonlim,xRes,yRes)
    Rasterize_shapefile(shapefile, raster_template, output_raster)


def Adjust_GRaND_reservoir(output_raster,WaPOR_LCC,GRaND_Reservoir,Resrv_to_Lake,Lake_to_Reserv):
#    output_raster,WaPOR_LCC,GRaND_Reservoir,Resrv_to_Lake,Lake_to_Reserv=_escape_str_paths(output_raster,WaPOR_LCC,GRaND_Reservoir,Resrv_to_Lake,Lake_to_Reserv)
     #Getting GeoTranformation from LCC map
    # driver,NDV,xsize,ysize,GeoT,Projection=gis.GetGeoInfo(WaPOR_LCC)
    # latlim=[GeoT[3]+ysize*GeoT[5],GeoT[3]]
    # lonlim=[GeoT[0],GeoT[0]+xsize*GeoT[1]]
    # xRes=GeoT[1]
    # yRes=-GeoT[5]
    #Rasterize selected area for reservoir and un-reservoir shapefile
    # Basin_reservoir=os.path.join(os.path.split(Resrv_to_Lake)[0],'Reservoir_GRanD.tif')
    # Rasterize_shapefile(GRaND_Reservoir,Basin_reservoir,
    #                             latlim,lonlim,xRes,yRes)
    # Rasterize_shapefile(Resrv_to_Lake,Resrv_to_Lake.replace('.shp','.tif'),
    #                             latlim,lonlim,xRes,yRes)

    # Rasterize_shapefile(Lake_to_Reserv,Lake_to_Reserv.replace('.shp','.tif'),
    #                             latlim,lonlim,xRes,yRes)
    Rasterize_shapefile(GRaND_Reservoir, WaPOR_LCC, Basin_reservoir)
    Rasterize_shapefile(Resrv_to_Lake, WaPOR_LCC, Resrv_to_Lake.replace('.shp','.tif'))
    Rasterize_shapefile(Lake_to_Reserv, WaPOR_LCC, Lake_to_Reserv.replace('.shp','.tif'))

    #Edit Resvr
    Resrv=gis.OpenAsArray(Basin_reservoir,nan_values=True)
    LCC=gis.OpenAsArray(WaPOR_LCC,nan_values=True)
    UnResrv=gis.OpenAsArray(Resrv_to_Lake.replace('.shp','.tif'),nan_values=True)
    MakeResrv=gis.OpenAsArray(Lake_to_Reserv.replace('.shp','.tif'),nan_values=True)

    Resrv=np.where(((LCC==80)*(MakeResrv==1)),1,Resrv)
    Resrv=np.where(((Resrv==1)*(UnResrv==1)),np.nan,Resrv)

#    output=os.path.join(os.path.split(Resrv_to_Lake)[0],'Reservoir_adjusted.tif')
    gis.CreateGeoTiff(output_raster, Resrv, driver, NDV, xsize, ysize, GeoT, Projection)
    return output_raster

def LCC_to_LUWA(WaPOR_LCC,Output_dir,ProtectedArea_tif,Reservoir_tif,LCC_LUWA_dict=None):
#    WaPOR_LCC,Output_dir,ProtectedArea_tif,Reservoir_tif=_escape_str_paths(WaPOR_LCC,Output_dir,ProtectedArea_tif,Reservoir_tif)
    if LCC_LUWA_dict is None:
        LCC_LUWA_dict={
                'PLU':(1,[]),
               'ULU':(2,[]),
               'MLU':(3,[41,42]),#Rainfed crop
               'MWU':(4,[42,50]), #irrigated crop and built-up
               }
    driver,NDV,xsize,ysize,GeoT,Projection=gis.GetGeoInfo(WaPOR_LCC)
    LCC=gis.OpenAsArray(WaPOR_LCC,nan_values=True)
    #ULU: The default is ULU
    LUWA=2*np.ones(np.shape(LCC),dtype=np.float32)
    #PLU: WDPA
    PLU=gis.OpenAsArray(ProtectedArea_tif,nan_values=True)
    LUWA=np.where(PLU==1,1,LUWA)
    #MLU: Rainfed crop => Modified Land Use
    for code in LCC_LUWA_dict['MLU'][1]:
        LUWA=np.where(LCC==code,3,LUWA)
    #MWU: Irrigated crop, Reservoir, Urban => Managed Water Use
    for code in LCC_LUWA_dict['MWU'][1]:
        LUWA=np.where(LCC==code,4,LUWA)
    MWU=gis.OpenAsArray(Reservoir_tif,nan_values=True)
    LUWA=np.where(MWU==1,4,LUWA)
    output_file=os.path.join(Output_dir,os.path.basename(WaPOR_LCC).replace('LCC','LUWA'))
    gis.CreateGeoTiff(output_file,LUWA,driver,NDV,xsize,ysize,GeoT,Projection)
#%% Reclassify function
#
#lcc=r"D:\FAO\WA_Sheet1\Input\Awash\L2_LCC_A\LCC_WAPOR.v2.0_level2_annually_2009.tif"
#lu=r"D:\Test\lu.tif"
#ProtectedArea=r"D:\FAO\WA_Sheet1\Input\Awash\ProtectedArea_WDPA.tif"
#Reservoir=r"D:\FAO\WA_Sheet1\Input\Awash\Reservoir\Reservoir_adjusted.tif"
#output_dir=r"D:\FAO\WA_Sheet1\Main\Awash\data"
#[ProtectedArea,Reservoir]=gis.MatchProjResNDV(lcc, [ProtectedArea,Reservoir], output_dir)


