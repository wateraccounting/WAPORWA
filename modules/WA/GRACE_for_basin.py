# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 16:08:05 2019

@author: Claire Michailovsky, Bert Coerver
For https://ssed.gsfc.nasa.gov/grace/products.html
GSFC.glb.200301_201607_v02.4-ICE6G

Modified by: Bich Tran
"""

import os
import csv
import datetime
import calendar
import ogr
import numpy as np
import pandas as pd
from shapely.geometry import Polygon, Point
import shapefile
from matplotlib import pyplot as plt

def main(Basin_shp,Dir_out,MASCON_folder,buffer=0.71):
    Basename=os.path.basename(Basin_shp).replace('.shp',r'')
    OUT_CSV=os.path.join(Dir_out,Basename+'.csv')
    
    BUFFER_SHP = os.path.join(Dir_out,Basename+'_buffer.shp')
    MASCON_SHP = os.path.join(Dir_out,Basename+'_mascons.shp')

    MASCON_INFO = os.path.join(MASCON_folder,'mascon.txt')
    MASCON_SOLUTION = os.path.join(MASCON_folder,'solution.txt')
    MASCON_DATES = os.path.join(MASCON_folder, 'time.txt')

    BUFFER_DIST = buffer
    _create_buffer(Basin_shp, BUFFER_SHP, BUFFER_DIST)
    df_info = pd.read_csv(MASCON_INFO, sep=r"\s+", header=None, skiprows=14,engine='python')
    mascon_coords = zip(df_info[1], df_info[0])
    
    df_dates = pd.read_csv(MASCON_DATES, sep=r"\s+", header=None, skiprows=13,engine='python')
    fract_dates = df_dates[2]
    mascon_dates = [str(_convert_partial_year(fdate)) for fdate in fract_dates]
    
    index_mascons_of_interest = _points_in_polygon(BUFFER_SHP, mascon_coords)
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
        lon_center = df_info[1][mascon_index]
        lat_center = df_info[0][mascon_index]
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
    basin_poly = ogr.Open(Basin_shp)
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
    
        return OUT_CSV

def __escape_str_paths(*args):
    outputs=[]
    for arg in args:
        new=arg.replace("\\","/")
        outputs.append(new)
    if len(outputs)==1:
        return outputs[0]
    else:
        return outputs
    
def _plot_shp(shp):
#    shp=__escape_str_paths(shp)
    sf = shapefile.Reader(shp)
    plt.figure()
    for shape in sf.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        plt.plot(x,y)
    plt.show()
# from ogr cookbook https://pcjericks.github.io/py-gdalogr-cookbook/layers.html
def _create_buffer(Basin_shp, BUFFER_SHP, BUFFER_DIST):
#    inputfn, output_bufferfn=__escape_str_paths(inputfn, output_bufferfn)
    inputds = ogr.Open(Basin_shp)
    inputlyr = inputds.GetLayer()

    shpdriver = ogr.GetDriverByName('ESRI Shapefile')
    if os.path.exists(BUFFER_SHP):
        os.remove(BUFFER_SHP)
        shpdriver.DeleteDataSource(BUFFER_SHP)
    outputBufferds = shpdriver.CreateDataSource(BUFFER_SHP)
    bufferlyr = outputBufferds.CreateLayer(BUFFER_SHP, geom_type=ogr.wkbPolygon)
    featureDefn = bufferlyr.GetLayerDefn()

    for feature in inputlyr:
        ingeom = feature.GetGeometryRef()
        geomBuffer = ingeom.Buffer(BUFFER_DIST)

        outFeature = ogr.Feature(featureDefn)
        outFeature.SetGeometry(geomBuffer)
        bufferlyr.CreateFeature(outFeature)
        outFeature = None

def _points_in_polygon(polyshp, pointcoords):
#    polyshp=__escape_str_paths(polyshp)
    polygon_r = shapefile.Reader(polyshp)
    polygon_shapes = polygon_r.shapes()
    shpfilePoints = []
    for shape in polygon_shapes:
        shpfilePoints = shape.points
    polygon_points = shpfilePoints
    polygon = Polygon(polygon_points)
    in_poly = []
    for coord in pointcoords:
        point = Point(coord)
        in_poly.append(polygon.contains(point))
    return np.where(np.array(in_poly))

### from bert
def _convert_partial_year(number):
    year = int(number)
    d = datetime.timedelta(days=(number - year)*(365 + calendar.isleap(year)))
    day_one = datetime.date(year, 1, 1)
    date = d + day_one
    return date