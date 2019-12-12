# WaPOR-based Water Accounting 
![](./img/README/1_banner.jpg)

Authors: 
- Bich Tran (b.tran@un-ihe.org)
- Solomon Seyoum 
- Claire Michailovsky 
- Bert Coever 

With contributions from:

- Marloes Mul
- Quan Pan 
- Elga Salvadore 
- Tim Hessels

## 1. About

This repository contains ipython notebooks, python scripts for the rapid Water Accounting analysis using WaPOR data in 5 river basins: Litani, Jordan, Awash, Niger, Nile. This work is done by the Water Accounting group at IHE-DELFT Institute for Water Education as a part of the WaPOR programme of The Food and Agriculture Organization of the United Nations (FAO).

http://www.fao.org/in-action/remote-sensing-for-water-productivity/overview/about-the-programme/en/

### 1.2. About WaPOR

Link: https://wapor.apps.fao.org/

FAO's web portal to monitor Water Productivity through Open-access of Remotely sensed derived data (WaPOR). This portal covers Africa and the Near East, with remotely sensed data, to monitor, in near real time, agricultural water and land productivity as well carbon dioxide uptake by vegetation.

For information about the programme, please visit: http://www.fao.org/in-action/remote-sensing-for-water-productivity/en/

### 1.3. About Water Accounting

Link: https://www.wateraccounting.org/

Water accounting is the process of communicating water resources related information and the services generated from consumptive use in a geographical domain, such as a river basin, a country or a land use class; to users such as policy makers, water authorities, managers, etc.

For more recent softwares developed by Water Accounting group at IHE-DELFT Institute for Water Education, please visit: https://github.com/wateraccounting

## 2. Description

### 2.1. Python requirements

### 2.2. Modules

#### 2.2.1. Workflow and notebooks
![](./img/README/2_workflow.png)

**Example notebooks**: Sample Case Study - Litani River Basin
- Run analysis: notebook
- Visualize results: notebook

#### 2.2.2. Pre-processing modules

- Create Landuse categories reclassification maps from WaPOR Landcover maps and other global maps
- Create Rootdepth map from WaPOR Landcover map and lookup table
- Calculate monthly number of rainy days from daily precipitation layers
- Calculate monthly data layers from dekadal ones
- Create input netCDF files

#### 2.2.3. Monthly Pixel-based Soil Moisture Balance module 
![](./img/README/3_pixelbased.png)

**See Model documentation**: To be updated (Wiki link)

#### 2.2.4. Basin fluxes calculation module

### 2.3. Inputs

#### 2.3.1. WaPOR data (v2.0)

| Data layers        | Resolution           | WAPOR cube_code  |
| ------------- |:-------------:| -----:|
| Precipitation      | Daily, 5km | L1_PCP_E |
| Precipitation      | Monthly, 5km      |   L1_PCP_M |
| Actual Evapotranspiration and Interception      | Monthly, 100m      |   L2_AETI_M |
| Interception      | Dekadal, 100m      |   L2_I_D |
| Land Cover Classification     | Yearly, 100m      |   L2_LCC_A |
| Reference Evapotranspiration      | Monthly, 20km      |   L2_RET_M |

#### 2.3.2. Other data

| Data layers       | Resolution           | Sources  |
| ------------- |:-------------:| -----:|
| Top soil saturated water content      | Static, 5km | HiHydroSoils |
| Protected Area      | Static, shapefile | WDPA |
| Reservoirs      | Static, shapefile | GRaND |
| Basin delineation      | Static, shapefile | HydroSHED |

| Data time-series        | Resolution           | Sources  |
| ------------- |:-------------:| -----:|
| Total Water Storage Change | Monthly, mascon | GRACE-GFCS |
| Observed flows      | Monthly, point | GRDC (unless mentioned otherwise) |

#### 2.3.3. Test dataset

Test dataset for Litani case: (to be uploaded)

### 2.4. Outputs

#### 2.4.1. Output data
| Data layers       | Resolution           | DataType  |
| ------------- |:-------------:| -----:|
| Incremental Evapotranspiration      | Monthly, 100m | netCDF |
| Rainfall Evapotranspiration      | Monthly, 100m | netCDF |
| Incremental Evapotranspiration      | Yearly, 100m | netCDF |
| Rainfall Evapotranspiration      | Yearly, 100m | netCDF |


| Data time-series        | Resolution           | DataType  |
| ------------- |:-------------:| -----:|
| WA+ Sheet 1 | Yearly, Basin | csv |
| P and ET per Land cover class | Yearly, LCC | csv |
| P and ET | Yearly, Basin | csv |

#### 2.4.2. Water Accounting Sheet 1: Resource Base

![](./img/OUTPUTS/1_sheet1sample.png)

**See Sheet 1 documentation**: To be updated (Wiki link)

#### 2.4.3. Water Accounting maps and charts

![](./img/OUTPUTS/2_P-ETpies.png)

![](./img/OUTPUTS/3_ETsplitperLCC.png)

![](./img/OUTPUTS/4_yearlyfluxes.png)

![](./img/OUTPUTS/5_yearlyET.png)

![](./img/OUTPUTS/6_averagemap.png)

![](./img/OUTPUTS/7_yearlymap.png)
