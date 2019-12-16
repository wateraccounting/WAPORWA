# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 10:21:22 2019

@author: ntr002
"""

# A script to rasterise a shapefile to the same projection & pixel resolution as a reference image.
import ogr 
import osr
import subprocess

#OutputFolder=r"D:\FAO\WA_Sheet1\Input\Awash"
#InputVector = r"D:\Others\Data\GRanD\GRanD_reservoirs_v1_1.shp"
#import os
#OutputRaster = os.path.join(OutputFolder,'Reservoir_GRaND.tif')
#latlim=[7.89,12.4] #miny,maxy
#lonlim=[37.95,43.35] #minx, maxx
#burnVal=1.0
#xRes=0.0009920634920000002618
#yRes=0.0009920634920000002618
#dataType='Float32'
#NDV=-9999.0

def Rasterize_shapefile(InputVector,OutputRaster,latlim,lonlim,xRes,yRes,
                        burnVal=1.0,layer=0,dataType='Float32',NDV=-9999.0):
    srs=osr.SpatialReference()
    srs.ImportFromEPSG(4326)
    a_srs=srs.ExportToWkt()
    dts=ogr.Open(InputVector)
    layer=dts.GetLayer(layer)
    layername=layer.GetDescription()
    extent='{0} {1} {2} {3}'.format(lonlim[0],latlim[0],lonlim[1],latlim[1])    
    string='gdal_rasterize -l {0} -burn {1} -tr {2} {3} -a_nodata {4} -a_srs {5} -te {6} -ot {7} -of GTiff {8} {9}'.format(layername,
                               burnVal,xRes,yRes,NDV,a_srs,extent,dataType,InputVector,OutputRaster)
    proc = subprocess.Popen(string, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return out, err

#Rasterize_shapefile(InputVector,OutputRaster,latlim,lonlim,xRes,yRes)
#options=gdal.RasterizeOptions(format='GTiff',outputType=gdal.GDT_Byte,noData=-9999.0,
#                              outputBounds=extent,layers=[layername],allTouched=True,
#                              burnValues=[1.0],outputSRS=srs,
#                              xRes=0.00223214286,yRes=0.00223214286)
#
#gdal.Rasterize(OutputImage,InputVector,options=options)

#'gdal_rasterize -l GRanD_dams_v1_1_buffer -burn 1.0 -tr 0.00223214286 0.002232 \
#-a_nodata -9999.0 -te -40.05 -30.5 40.05 65.05 -ot Float32 \
#-of GTiff D:/Others/Data/GRanD/GRanD_dams_v1_1_buffer.shp \
#D:/Others/Data/GRanD/GRanD_dams_v1_1_buffer.tif'