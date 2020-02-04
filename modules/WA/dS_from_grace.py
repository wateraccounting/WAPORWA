# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 12:46:12 2019

@author: Claire Michailovsky, Bert Coerver, Bich Tran

This script is used to calculate the basin mean TWSA from GRACE GFSC product mascon values.

Need to download global GRACE GFSC product from
https://ssed.gsfc.nasa.gov/grace/products.html
GSFC.glb.200301_201607_v02.4-ICE6G - ASCII

!!NOTICE: The Basin shapefile must be EPSG4326 projected, single polygon with no null geometry, holes, etc...

Use fix_shapefile_Qpy.py in QGIS processing script to fix input shapefile

"""
import os
import csv
import pandas as pd
import numpy as np
import datetime
import calendar

#!MUST Import shapefile and shapely before osgeo
#https://github.com/geopandas/geopandas/issues/556#issuecomment-565504722
import shapefile
import shapely.geometry as geometry

import osgeo.ogr as ogr
# from ogr cookbook https://pcjericks.github.io/py-gdalogr-cookbook/layers.html

##functions
def create_buffer(inputfn, output_bufferfn, buffer_dist):
    inputds = ogr.Open(inputfn)
    inputlyr = inputds.GetLayer()

    shpdriver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(output_bufferfn):
        os.remove(output_bufferfn)
        shpdriver.DeleteDataSource(output_bufferfn)
    outputBufferds = shpdriver.CreateDataSource(output_bufferfn)
    bufferlyr = outputBufferds.CreateLayer(output_bufferfn, geom_type=ogr.wkbPolygon)
    featureDefn = bufferlyr.GetLayerDefn()

    for feature in inputlyr:
        ingeom = feature.GetGeometryRef()
        geomBuffer = ingeom.Buffer(buffer_dist)

        outFeature = ogr.Feature(featureDefn)
        outFeature.SetGeometry(geomBuffer)
        bufferlyr.CreateFeature(outFeature)
        outFeature = None
    outputBufferds=None #close shapefile

def points_in_polygon(polyshp, pointcoords):
    polygon_r = shapefile.Reader(polyshp)
    polygon_shapes = polygon_r.shapes()
    shpfilePoints = polygon_shapes[0].points 
    #assume shapefile only has 1 shape
    polygon = geometry.Polygon(shpfilePoints)
    in_poly = []
    for coord in pointcoords:
        point=geometry.Point(coord)
        in_poly.append(polygon.contains(point))
    points_indices=np.where(np.array(in_poly))  
    polygon_r=None #close
    return points_indices


### from bert
def convert_partial_year(number):
    year = int(number)
    d = datetime.timedelta(days=(number - year)*(365 + calendar.isleap(year)))
    day_one = datetime.date(year, 1, 1)
    date = d + day_one
    return date

def read_mascon_info(MASCON_DATA_FOLDER):
    MASCON_INFO = os.path.join(MASCON_DATA_FOLDER, 'mascon.txt')
    MASCON_DATES = os.path.join(MASCON_DATA_FOLDER, 'time.txt')
    #mascon info coordinates
    df_info = pd.read_csv(MASCON_INFO, sep=r"\s+", 
                          header=None, skiprows=14,engine='python')
    lat=df_info[0]
    #convert lon from (0,360) to (-180,180)
    lon=df_info[1].where(df_info[1]<180,df_info[1]-360) 
    
    mascon_coords = list(zip(lon,lat))
    #mascon dates
    df_dates = pd.read_csv(MASCON_DATES, sep=r"\s+", 
                           header=None, skiprows=13,engine='python')
    fract_dates = df_dates[2]
    mascon_dates = [str(convert_partial_year(fdate)) for fdate in fract_dates]
    return df_info,mascon_coords,mascon_dates

def main(BASIN_SHP,MASCON_DATA_FOLDER,OUT_CSV,BUFFER_DIST=.71):
    """
    Description

    """
#    BASIN_SHP=r"D:\Data\GRACE\Niger_GRACE\Niger.shp"
#    OUT_CSV=r"D:\Data\GRACE\Niger_GRACE\Niger.csv"
#    MASCON_DATA_FOLDER = r"D:\Data\GRACE\GSFC.glb.200301_201607_v02.4-ICE6G"
    
    BUFFER_SHP = OUT_CSV.split('.')[:-1][0]+'_buffer.shp'
    MASCON_SHP = OUT_CSV.split('.')[:-1][0]+'_mascons.shp'
    
    MASCON_SOLUTION = os.path.join(MASCON_DATA_FOLDER, 'solution.txt')
    
    ## Create buffer 
    create_buffer(BASIN_SHP, BUFFER_SHP, BUFFER_DIST)
    
    ## Read mascon info
    df_info,mascon_coords,mascon_dates=read_mascon_info(MASCON_DATA_FOLDER)
    
    #pointcoords=mascon_coords
    #polyshp=BUFFER_SHP
    
    ## Select mascon of interest
    index_mascons_of_interest = points_in_polygon(BUFFER_SHP,                                              mascon_coords)
    
    data_lines = []
    with open(MASCON_SOLUTION) as fp:
        for i, line in enumerate(fp):
            if i in np.array(index_mascons_of_interest) + 7:
                data_lines.append(np.array(line.rstrip('\n').rstrip().split(' ')).astype(float))
    
    # Create .shp of mascon areas
    # Adapeted from bec's SortGRACE.py
    w = shapefile.Writer(MASCON_SHP, shapeType=shapefile.POLYGON)
    w.field('MASCON_ID', 'C', '40')
    
    for mascon_index in index_mascons_of_interest[0]:
        ID = mascon_index+1
        lon_center = mascon_coords[mascon_index][0]
        lat_center = mascon_coords[mascon_index][1]
        lon_span = df_info[3][mascon_index]
        lat_span = df_info[2][mascon_index]
        w.poly([
                [[lon_center + .5 * lon_span, lat_center + .5 * lat_span],
                 [lon_center - .5 * lon_span, lat_center + .5 * lat_span],
                 [lon_center - .5 * lon_span, lat_center - .5 * lat_span],
                 [lon_center + .5 * lon_span, lat_center - .5 * lat_span],
                 [lon_center + .5 * lon_span, lat_center + .5 * lat_span]]
                ])
        w.record(ID,'Polygon')
    w.close()
    # Get weights from relative intersection area
    basin_poly = ogr.Open(BASIN_SHP)
    mascon_poly = ogr.Open(MASCON_SHP)
    
    basin_lyr = basin_poly.GetLayer()
    mascon_lyr = mascon_poly.GetLayer()
    for b_feature in basin_lyr:
        ids = []
        int_area = []
        total_area = 0
        for m_feature in mascon_lyr:
            b_geom = b_feature.GetGeometryRef()
            m_geom = m_feature.GetGeometryRef()
            test = b_geom.Intersection(m_geom)
            ids.append(m_feature.GetField(0))
            int_area.append(test.GetArea())
            total_area += test.GetArea()
            
    weights = np.array(int_area)/total_area
    
    weighted_line = [data_lines[i] * weights[i] for i in range(len(data_lines))]
    weighted_average = np.sum(weighted_line, 0)
    
    with open(OUT_CSV, 'w',newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        spamwriter.writerow(['date', 'Equivalent Water Height [mm]'])
        for date, value in zip(mascon_dates, weighted_average):
            spamwriter.writerow([date, value*10])
    return True

