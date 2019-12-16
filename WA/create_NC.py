# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 12:04:54 2019

@author: ntr002

Adapted from Bert Coerver and Claire Michailovsky


"""
import os
import gdal
import numpy as np
import tempfile
import ogr
import gzip
import zipfile
import netCDF4
import csv
import datetime
import calendar
from dateutil.relativedelta import relativedelta
import glob
import itertools
from .find_possible_date import find_year,find_month,find_date
from tqdm import tqdm
import osr
import shutil

def main(nc_fn,basin,dataset,template,cutline,step='month',**kwargs):
    '''
    filename: str
        output netCDF file name
    dataset:
        {'P'        : [r'F:\Exercise\1.4\Monthly\L1_PCP_M',
                               ('time','latitude', 'longitude'), 
                               {'units': 'mm/month', 'source': 'WaPOR', 
                                'quantity':'P','period':'month'}]}
    template: str
        file handler to template raster
    cutline: str
        file handler to shapefile
    DTindex: object
        pandas DatetimeIndex range
    '''
    dims = {'time':  None, 'latitude': None, 'longitude': None}
    dims['latitude'], dims['longitude'], optionsProj, optionsClip = _get_lats_lons(template, cutline)
    _init_nc(nc_fn, dims, dataset, attr = {"basin_name" : basin})
    overview=_make_overview(dataset, step)
    succes = _fill_data_to_nc(nc_fn, overview, optionsProj, optionsClip, cutline)
    return succes

def _init_nc(nc_file, dim, var, fill = -9999., attr = None):
    # Create new nc-file. Existing nc-file is overwritten.
    out_nc = netCDF4.Dataset(nc_file, 'w', format='NETCDF4')
    
    # Add dimensions to nc-file.
    for name, values in dim.items():
        # Create limited dimensions.
        if values is not None:
            out_nc.createDimension(name, values.size)
            vals = out_nc.createVariable(name, 'f4', (name,), fill_value = fill)
            vals[:] = values
        # Create unlimited dimensions.
        else:
            out_nc.createDimension(name, None)
            vals = out_nc.createVariable(name, 'f4', (name,), fill_value = fill)
            vals.calendar = 'standard'
            vals.units = 'days since 1970-01-01 00:00'
    
    # Create variables.
    for name, props in var.items():
        vals = out_nc.createVariable(props[2]['quantity'], 'f4', props[1], zlib = True, 
                                     fill_value = fill, complevel = 9, 
                                     least_significant_digit = 3)
        vals.setncatts(props[2])


    if attr != None:
        out_nc.setncatts(attr)

    # Close nc-file.
    out_nc.close()
    
def _get_lats_lons(example, shape):
   
    gdal.UseExceptions()
    
    # Create temporary tif-file.
    temp_file = tempfile.NamedTemporaryFile(suffix='.tif').name
    
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(shape, 1)
    inLayer = inDataSource.GetLayer()

    options = gdal.WarpOptions(cutlineDSName = shape,
                               cutlineLayer = inLayer.GetName(),
                               cropToCutline = False,
                               dstNodata = -9999,
                               )
    
    sourceds = gdal.Warp(temp_file, example, options = options)

    geot    = sourceds.GetGeoTransform()
    xsize   = sourceds.RasterXSize # columns
    ysize   = sourceds.RasterYSize # rows
    
    lons = np.arange(geot[0], (geot[0] + xsize * geot[1]) - geot[1] + 1e-10, geot[1]) + 0.5 * geot[1]
    lats = np.arange(geot[3], (geot[3] + ysize * geot[5]) - geot[5] - 1e-10, geot[5]) + 0.5 * geot[5]

    minX = geot[0]
    minY = geot[3] + ysize * geot[5]
    maxX = geot[0] + xsize * geot[1]
    maxY = geot[3]
    
    assert lats.size == ysize
    assert lons.size == xsize
    
    print(np.diff(lats)[0] - geot[5])
    print(np.diff(lons)[0] - geot[1])

    optionsProj = gdal.WarpOptions(
                               outputBounds = (minX, minY, maxX, maxY),
                               width = xsize,
                               height = ysize,
                               dstNodata = -9999,
                               options = ["GDALWARP_IGNORE_BAD_CUTLINE YES"],
                               )

    optionsClip = gdal.WarpOptions(
                               cutlineDSName = shape,
                               cutlineLayer = inLayer.GetName(),
                               cropToCutline = False,
                               outputBounds = (minX, minY, maxX, maxY),
                               width = xsize,
                               height = ysize,
                               dstNodata = -9999,
                               options = ["GDALWARP_IGNORE_BAD_CUTLINE YES"],
                               )
    
    return lats, lons, optionsProj, optionsClip

def _fill_data_to_nc(nc_file, overview, optionsProj, optionsClip, shape):

    # Save the time-invariant data to nc-file.
    if "invariant" in overview.keys():
        invar = overview.pop("invariant")
        var = dict()
        for fh in [x for x in invar if x is not None]:
            temp_file = tempfile.NamedTemporaryFile(suffix='.tif').name
            temp_fileP = tempfile.NamedTemporaryFile(suffix='.tif').name
#            sourceds = gdal.Warp(temp_file, fh[1], options = options)
            gdal.Warp(temp_fileP, fh[1], options = optionsProj)
            sourceds = gdal.Warp(temp_file, temp_fileP, options = optionsClip)
            var[fh[0]] = sourceds.ReadAsArray()
            sourceds = None
            os.remove(temp_file)
            os.remove(temp_fileP)
        __fill_nc_one_timestep(nc_file, var, shape)
    
    # Save time-variant data to nc-file.
    for date in tqdm(overview.keys()):
        var = dict()
        for fh in [x for x in overview[date] if x is not None]:
            # Reproject and open tif-file for a specific date.
            if isinstance(fh[1], str):
                ext = fh[1].split('.')[-1].split(":")[0]
                
                if ext == 'gz':
                    path = __ungz(fh[1])
                elif ext == 'zip':
                    path = __unzip(fh[1])
                else:
                    path = fh[1]
                    
#                assert "GDAL_DATA" in os.environ
                
                path = __check_projection(path)
                temp_file = tempfile.NamedTemporaryFile(suffix='.tif').name
                temp_fileP = tempfile.NamedTemporaryFile(suffix='.tif').name       
                
                gdal.Warp(temp_fileP, path, options = optionsProj)
                sourceds = gdal.Warp(temp_file, temp_fileP, options = optionsClip)
                var[fh[0]] = sourceds.ReadAsArray().astype(np.float32)
                
                if ext == 'nc':
                    var_name = fh[0]
                    scale = sourceds.GetMetadataItem("{0}#scale_factor".format(var_name))
                    offset = sourceds.GetMetadataItem("{0}#add_offset".format(var_name))
                    if scale is not None and offset is not None:
                        var[fh[0]][var[fh[0]] != -9999] *= float(scale)
                        var[fh[0]][var[fh[0]] != -9999] += float(offset)

                sourceds = None
                os.remove(temp_file)
                os.remove(temp_fileP)
                if ext in ['gz', 'zip']:
                    os.remove(path)

            # Open non-spatial data for a specific date.
            elif isinstance(fh[1], float):
                var[fh[0]] = fh[1]
            else:
                continue
        #fill_nc_one_timestep(nc_file, var, shape, date.toordinal())
        __fill_nc_one_timestep(nc_file, var, shape, np.datetime64(date))
        
    return True

def _make_overview(datasets, step, start = None, end = None):
    # Loop over the folders with tif-files and extract the date from the filenames.
    data_inventory = dict()
    
    for name1, ds in datasets.items():
        name = datasets[name1][2]['quantity']
        ds = ds[0]

        inventory = dict()
        
        # Make inventory of data from csv-files.
        if np.all([os.path.isfile(ds), os.path.splitext(ds)[1] == ".csv"]):
            with open(ds) as csv_file:
                csv_reader = csv.reader(csv_file)
                header_rows = 12
                [next(csv_reader) for x in range(header_rows)] # skip header rows
                for row in csv_reader:
                    yr, dc = row[0].split('.')
                    year = int(yr)
                    dec = float('0.' + dc)
                    year_length = {True: 366, False:365}[calendar.isleap(int(year))]
                    date = datetime.date(year, 1, 1) + relativedelta(days = dec * year_length)
                    value = float(row[1]) * 10 #cm to mm
                    inventory[date] = (name, value)

        # Make inventory of invariant spatial data.
        elif np.all([os.path.isfile(ds), os.path.splitext(ds)[1] == ".tif"]):
            inventory["invariant"] = (name, ds)
        
        # Make inventory of variant spatial data.
        elif os.path.isdir(ds):            
            fhs, form = __select_files(ds, possible_formats = ['.tif', '.zip', '.gz', '.nc'])
            
            for fh in fhs:
                if step=='month':
                    date,_,_ = find_month(fh)
                elif step=='year':
                    date,_ = find_year(fh)
                elif step=='day':
                    date,_,_,_= find_date(fh)
                    
                if form == '.nc':
                    fh = "NETCDF:{0}:{1}".format(fh, name)

                inventory[date] = (name, fh)
        
        # Skip data that does match above criteria.
        else:
            print("skipping {0}".format(ds))
            continue
        
        data_inventory[name] = inventory
    
    # Create dictionary with list of availables tif-files as values for each date (key).
    overview = {}
    for k in itertools.chain(*[x.keys() for x in data_inventory.values()]):
        if isinstance(k, str) or ((start is None or start <= k) and (end is None or end >= k)):
            overview[k] = [x.get(k, None) for x in data_inventory.values()]
        
    return overview

def __fill_nc_one_timestep(nc_file, var, shape, time_val = None):
    # Open existing nc-file.
    out_nc = netCDF4.Dataset(nc_file, 'r+')
    varis = out_nc.variables.keys()
    dimis = out_nc.dimensions.keys()
    
    # Add time-dependent data to nc-file.
    if time_val is not None:
        time = out_nc.variables['time']
        tidx = time.shape
        time[tidx] = time_val
        
        for name in [x for x in varis if "time" in out_nc[x].dimensions and x not in dimis]:
            field = out_nc.variables[name]
            if name in var.keys():
                field[tidx,...] = var[name]
            else:
                shape = tuple([y for x, y in enumerate(out_nc[name].shape) if out_nc[name].dimensions[x] != "time"])
                dummy_data = np.ones(shape) * out_nc[name]._FillValue
                field[tidx,...] = dummy_data
    
    # Add invariant data to nc-file.
    else:
        for name, data in var.items():
            out_nc.variables[name][...] = data
    
    # Close nc-file.
    out_nc.close()
    
def __check_projection(old_path):
    
    ds=gdal.Open(old_path)
    prj=ds.GetProjection()
    ds = None
    
    if len(prj) == 0:
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        path = tempfile.NamedTemporaryFile(suffix='.vrt').name
        gdal.Translate(path, old_path, outputSRS = srs)
    else:
        path = old_path

    return path   
 
def __select_files(folder, possible_formats = ['.tif', '.zip', '.gz', '.nc']):
    """
    Search a folder for files with extensions defined by 'possible_formats'
    and return a list of files with the most frequent occuring extension. If
    multiple extensions are present inside the folder with equal frequency, the
    returned extension is chosen arbitraraly (and a message is printed).
    """
    search = os.path.join(folder, "*")
    formats = np.unique([os.path.splitext(x)[1] for x in glob.glob(search)], return_counts = True)
    
    maxi = np.max([y for x, y in zip(formats[0], formats[1]) if x in possible_formats])
    
    form = formats[0][formats[1] == maxi]
    if form.size > 1:
        print("Multiple valid file-formats in folder ('{0}'), selecting {1}-files only.".format(folder, form[0]))
    form = "*" + form[0]

    return glob.glob(os.path.join(folder, form)), form[1:]

def __ungz(path):
    with gzip.open(path, 'rb') as f_in:
        temp_file = tempfile.NamedTemporaryFile(suffix='.tif').name
        with open(temp_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return temp_file

def __unzip(path):
    zip_ref = zipfile.ZipFile(path, 'r')
    tif_files = [x for x in zip_ref.namelist() if x[-3:] == 'tif']
    assert len(tif_files) == 1, "zip-file ({0}) contains multiple tif-files".format(path)
    folder = tempfile.tempdir
    temp_file = zip_ref.extract(tif_files[0], path = folder)
    return temp_file

