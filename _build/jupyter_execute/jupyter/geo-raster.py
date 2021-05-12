#!/usr/bin/env python
# coding: utf-8

# # Raster (Gridded) Dataset Handling
# 
# Geospatial analysis of raster (gridded) data with gdal and rasterstats. For interactive reading and executing code blocks [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/hydro-informatics/hydro-informatics.github.io/main?filepath=jupyter) and find *geo-raster.ipynb* or {ref}`install-python` locally along with {ref}`jupyter`.
# 
# Make sure to understand [gridded raster data](geospatial-data.html#raster) before reading this section. Recall that we will mostly deal with the `.tif` (*GeoTIFF*) format for grid data and hat many other raster data types exist.
# 
# ```{admonition} Tips
# * While `gdal`'s `ogr` module is useful for shapefile handling, raster data are best handled by `gdal` itself.
# * Download sample raster datasets from [*River Architect*](https://github.com/RiverArchitect/SampleData/archive/master.zip). This page uses *GeoTIFF* raster data located in [`RiverArchitect/SampleData/01_Conditions/2100_sample/`](https://github.com/RiverArchitect/SampleData/tree/master/01_Conditions/2100_sample).
# * The core functions used in this e-book are introduced with the raster and vector data handling explanations and additionally implemented in the {{ ft_url }} package.
# ```
# 
# ## Load raster
# 
# (open-raster)=
# ### Open Existing Raster Data 
# 
# Raster data can be opened as a `gdal.Open("FILENAME")` object. The following code block provides a function to open any raster specified with the `file_name` input argument. One of the most important elements when dealing with raster data is the `RasterBand`, which takes on a similar data carrier role as `GetLayer` in shapefile handling.
# To create this important object, the `open_raster` function:
# 
# 1. Enables error and warning feedback with `gdal.UseExceptions()` (this step is absolutely vital when using raster data).
# 1. Opens the provided raster `file_name` embraced by `try` - `except` statements to inform if and why an error occurred while opening the raster.
# 1. Opens the raster band number stated in the optional `band_number` keyword argument with `raster_band = raster.GetRasterBand(band_number)` (the default value is `1`).
# 1. Returns the raster and raster band objects.
# 

# In[1]:


import gdal


def open_raster(file_name, band_number=1):
    """
    Open a raster file and access its bands
    :param file_name: STR of a raster file directory and name
    :param band_number: INT of the raster band number to open (default: 1)
    :output: osgeo.gdal.Dataset, osgeo.gdal.Band objects
    """
    gdal.UseExceptions()
    # open raster file or return None if not accessible
    try:
        raster = gdal.Open(file_name)
    except RuntimeError as e:
        print("ERROR: Cannot open raster.")
        print(e)
        return None
    # open raster band or return None if corrupted
    try:
        raster_band = raster.GetRasterBand(band_number)
    except RuntimeError as e:
        print("ERROR: Cannot access raster band.")
        print(e)
        return None
    return raster, raster_band


# To use the `open_raster` function just call it with a file name as shown in the following code block with the `h001000.tif` raster from the [*River Architect* sample data](https://github.com/RiverArchitect/SampleData/archive/master.zip). The script immediately closes the raster again by overwriting it with `None` to avoid that the file is locked afterwards.

# In[2]:


import os
file_name = r"" + os.getcwd() + "/geodata/river-architect/h001000.tif"
src, depth = open_raster(file_name)
print(src)
print(depth)
depth = None


# ### Raster Band Statistics and Toolbox Scripts
# 
# Once we loaded a raster and a raster band with the above `open_raster` function, we can access statistical information (e.g., the minimum or the maximum), identify the *no-data* value (i.e., a pre-defined value that is assigned to pixels without value), or the type of units used.
# 
# *Python* scripts for processing geospatial data can also be embedded as plugins in *GIS* desktop applications (e.g., as plugins in *QGIS* or *Toolbox* in *ArcGIS Pro*). To run a *Python* script in a *GIS* desktop application, it should be written as a standalone script that can receive input arguments. Creating plugins is not a primary learning goal here and the interested reader can read more about implementing plugins in *QGIS* in the [*QGIS* docs](https://docs.qgis.org/3.10/en/docs/pyqgis_developer_cookbook/plugins/index.html).
# 
# ```{note}
# In fact, *QGIS* wraps many external functionalities, which are available through he *QGIS Processing Toolbox*. The provided algorithms belong for example to *SAGA* or *GRASS GIS*.
# ```
# 
# Here we will only write the next code block so that it can be run in a console/terminal application as standalone script (recall the [instructions to writing standalone script](../python-basics/pypckg.html#standalone)).

# ```python
# # make sure to use exceptions
# gdal.UseExceptions()
# 
# def how2use():
#     # provide usage instructions for the script
#     print("""
#     $ raster_band_info.py [ band number ] input-raster
#     """)
#     # exit program if wrong input arguments provided
#     sys.exit(1)
#     
# 
# def get_color_bands(raster_band):
#     """
#     :param raster_band: osgeo.gdal.Band object
#     :output: list of color bands used in raster_band
#     """ 
#     
#     # get ColorTable and return False if None
#     color_table = raster_band.GetColorTable()
#     if color_table is None:
#         print("Band has no ColorTable.")
#         return None
#     else:
#         print("Found %i color definitions." % int(color_table.GetCount()))
# 
#     # iterate through color_table and append objects found to colors_bands list
#     color_bands = []
#     for c in range(0, color_table.GetCount() ):
#         entry = color_table.GetColorEntry(c)
#         if not entry:
#             continue
#         color_bands.append(str(color_table.GetColorEntryAsRGB(c, entry)))
#     return color_bands
# 
# def main(band_number, input_file):
#     src, band = open_raster(input_file)
#     print("Band minimum: ", band.GetMinimum())
#     print("Band maximum: ", band.GetMaximum())
#     print("No-data value: ", band.GetNoDataValue())
#     print("Band unit type: ", band.GetUnitType())    
# 
#     try:
#         print(", ".join(get_color_bands(band)))
#     except TypeError:
#         print("ColorTable: None")
# 
# if __name__ == '__main__':
#     # make standalone
#     if len( sys.argv ) < 3:
#         print("""
#         ERROR: Provide two arguments:
#         1) the band number (int) and 2) input raster directory (str)
#         """)
#         how2use()
# 
#     main(int(sys.argv[1]), str(sys.argv[2]))
# ```

# To run this script, save it as `raster_band_info.py` (e.g., in `C:\temp`) and navigate to the script directory in a terminal application (e.g., in *PyCharm*'s *Terminal*) using the `cd` command. Now run the script to get information of the water depth raster `h001000.tif` with:

# ```
# C:\temp\ python raster_band_info.py 1 "C:\temp\geodata\river-architect\h001000.tif"
# ```

# ```
# Band minimum:  0.0
# Band maximum:  7.0613012313843
# No-data value:  -3.4028234663852886e+38
# Band unit type:
# Band has no ColorTable.
# ColorTable: None
# ```

# ## Create and Save a Raster (from Array)
# 
# (raster-drivers)=
# ### Raster Drivers
# 
# Just like for shapefile files, the appropriate `gdal` driver (analogous to `ogr` drivers) must be loaded to save a raster. To get a full list of `gdal` drivers run:

# In[3]:


driver_list = [str(gdal.GetDriver(i).GetDescription()) for i in range(gdal.GetDriverCount())]
driver_list.sort()
print(", ".join(driver_list[:]))


# (etypes)=
# ### Raster Data Types 
# 
# The output raster pixels can have the following data types (source: [gdal.org/doxygen/](https://gdal.org/doxygen/classGDALDataset.html)):
# * `GDT_Unknown` Unknown or unspecified type
# * `GDT_Byte` 8 bit unsigned integer
# * `GDT_UInt16` 16 bit unsigned integer
# * `GDT_Int16` 16 bit signed integer
# * `GDT_UInt32` 32 bit unsigned integer
# * `GDT_Int32` 32 bit signed integer
# * `GDT_Float32` 32 bit floating point
# * `GDT_Float64` 64 bit floating point
# * `GDT_CInt16` Complex Int16
# * `GDT_CInt32` Complex Int32
# * `GDT_CFloat32` Complex Float32
# * `GDT_CFloat64` Complex Float64 

# (create-raster)=
# ### Create Raster (Array to Raster) 
# 
# With these ingredients, we can create a raster from a numeric array, because a raster is basically just a georeferenced array. In *Python* it is convenient to convert a [*numpy* array](../python-basics/pynum.html#array-matrix-operations) into a raster (band). The following functions features the conversion of a *numpy* array into a *GeoTIFF* rasters with the following workflow:
# 
# 1. Check out the *GeoTIFF* driver (`driver = gdal.GetDriverByName('GTiff')`).
# 1. Retrieve the array size and (number of rows `rows` and columns `cols`).
# 1. Create a new *GeoTIFF* raster (`new_raster = driver.Create(file_name, cols, rows, 1, eType=rdtype)`), where 
#     - `file_name` is the directory and name of the new raster file ending on `.tif` (e.g., `"C:\\temp\\rasters\\new.tif"`).
#     - `cols`, `rows` represent the array shape, and `eType` is the geospatial data type (see above list)
# 1. Set the geographic origin stored in the `origin` (*tuple*) parameter and define the `pixel_width` and `pixel_height` (pixel units defined with `srs` - see below).
# 1. Replace `np.nan` values in array with `nan_value`.
# 1. Instantiate a `band` object, set the the `NoDataValue` to `nan_value`, and write the array to the `band`.
# 1. Create a spatial reference system object  (`srs`) as a function of the `epsg` input parameter and export it to *WKT* format.
# 1. Release the raster (flush from cache).
# 
# ```{note}
# The units defined with the `epsg` projection drive the pixel size, where `pixel_width` and `pixel_height` are multipliers of that unit. In the case of `epsg=3857`, the unit is `meters` and `pixel_width=10` combined with `pixel_height=20` creates 10m wide and 20m high pixels. In the case of `epsg=4326`, the unit is (geographic) `degrees` and 1 degree by 1 degree pixels can have the size of a county.
# ```

# In[4]:


import osr


def create_raster(file_name, raster_array, origin=None, epsg=4326, pixel_width=10, pixel_height=10,
                  nan_value=-9999.0, rdtype=gdal.GDT_Float32, geo_info=False):
    """
    Convert a numpy.array to a GeoTIFF raster with the following parameters
    :param file_name: STR of target file name, including directory; must end on ".tif"
    :param raster_array: np.array of values to rasterize
    :param origin: TUPLE of (x, y) origin coordinates
    :param epsg: INT of EPSG:XXXX projection to use - default=4326
    :param pixel_height: INT of pixel height (multiple of unit defined with the EPSG number) - default=10m
    :param pixel_width: INT of pixel width (multiple of unit defined with the EPSG number) - default=10m
    :param nan_value: INT/FLOAT no-data value to be used in the raster (replaces non-numeric and np.nan in array)
                        default=-9999.0
    :param rdtype: gdal.GDALDataType raster data type - default=gdal.GDT_Float32 (32 bit floating point)
    :param geo_info: TUPLE defining a gdal.DataSet.GetGeoTransform object (supersedes origin, pixel_width, pixel_height)
                        default=False
    """
    # check out driver
    driver = gdal.GetDriverByName('GTiff')

    # create raster dataset with number of cols and rows of the input array
    cols = raster_array.shape[1]
    rows = raster_array.shape[0]
    new_raster = driver.Create(file_name, cols, rows, 1, eType=rdtype)    

    # apply geo-origin and pixel dimensions
    if not geo_info:
        origin_x = origin[0]
        origin_y = origin[1]
        new_raster.SetGeoTransform((origin_x, pixel_width, 0, origin_y, 0, pixel_height))
    else:
        new_raster.SetGeoTransform(geo_info)
    
    # replace np.nan values
    raster_array[np.isnan(raster_array)] = nan_value

    # retrieve band number 1
    band = new_raster.GetRasterBand(1)
    band.SetNoDataValue(nan_value)
    band.WriteArray(raster_array)
    band.SetScale(1.0)

    # create projection and assign to raster
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    new_raster.SetProjection(srs.ExportToWkt())

    # release raster band
    band.FlushCache()


# To call the function for writing a random *numpy* array, we can now use the `create_raster` function:

# In[5]:


# set the name of the output GeoTIFF raster
raster_name = r"" + os.getcwd() + "/geodata/rasters/random_unis_dem.tif"
# create a random numpy array (DEM-like values) - can be replaced with any other numpy.array
unis_dem = np.random.rand(300, 300) + 455.0
# overwrite one pixel with np.nan
unis_dem[5, 7] = np.nan
# define a raster origin in EPSG:3857
raster_origin = (1013428.396233, 6231555.006177)
# call create_raster to create a 1-m-resolution raster in EPSG:4326 projection
create_raster(raster_name, unis_dem, raster_origin,  pixel_width=1,  pixel_height=1, epsg=3857) 


# ![img](https://raw.githubusercontent.com/sschwindt/hydroinformatics/main/docs/img/qgis-ras-unis.png)

# (createarray)=
# ### Raster Calculus (Raster / Band to Array) 
# 
# The procedure described in the create_raster function above can be used in a similar way to create [*numpy* array](../python-basics/pynum.html#array-matrix-operations) from raster bands.
# This enables algebraic or other logical operations to be applied to existing raster data. Need an example? In the *RiverArchitect SampleData*, the units of the water depth raster `h001000.tif` are in U.S. customary feet and the units of the flow velocity raster `u001000.tif` are in feet per second. To calculate the *Froude* number (recall the meaning of the [*Froude* number in the data processing section](../python-basics/pynum.html#exp-Froude)) for each pixel based on the two rasters (water depth and flow velocity), it is convenient to convert both rasters into m and m/s, respectively.
# 
# First we want to write a custom function that loads a raster as an array and overwrites `NoDataValues` with `np.nan` (`raster` and `band` can be instantiated with the above `open_raster` function):

# In[6]:


def raster2array(file_name, band_number=1):
    """
    :param file_name: STR of target file name, including directory; must end on ".tif"
    :param band_number: INT of the raster band number to open (default: 1)
    :output: (1) ndarray() of the indicated raster band, where no-data values are replaced with np.nan
             (2) the GeoTransformation used in the original raster
    """
    # open the raster and band (see above)
    raster, band = open_raster(file_name, band_number=band_number)
    # read array data from band
    band_array = band.ReadAsArray()
    # overwrite NoDataValues with np.nan
    band_array = np.where(band_array == band.GetNoDataValue(), np.nan, band_array)
    # return the array and GeoTransformation used in the original raster
    return raster, band_array, raster.GetGeoTransform()


# ```{admonition} Challenge
# The `raster2array` function returns a tuple, where `output[0]` corresponds to the array and `output[1]` is the geo-transformation. Can you optimize the way how these information is returned?
# ```
# 
# The following code block makes use of the `raster2array` function for converting a *GeoTIFF* raster into a *numpy* array, performs simple algebraic calculations, and saves the result in the shape of a *Froude* number *GeoTIFF* raster. In detail, the workflow involves to: 
# 
# * Define the input raster file names with directories (`h_file` and `u_file`),
# * Load original rasters as `ndarray` with the `raster2array` function and get the original `GeoTransform` description,
# * converts all values from U.S. customary feet to S.I. metric (recall the [`feet_to_meter`](../python-basics/pyfun.html#kwargs) function from the *Python* basics), and
# * saves a new copy of the raster.

# In[7]:


h_file = r"" + os.getcwd() + "/geodata/river-architect/h001000.tif"
u_file = r"" + os.getcwd() + "/geodata/river-architect/u001000.tif"

# load both rasters as arrays
h_ras, h, h_geo_info = raster2array(h_file)
u_ras, u, u_geo_info = raster2array(u_file)

#convert to metric system
h *= 0.3048
u *= 0.3048

# calculate the Froude number as array and avoid zero-division warning messages
with np.errstate(divide="ignore", invalid="ignore"):
    Froude = u / np.sqrt(h * 9.81)

# create Froude raster from array
create_raster(file_name= r"" + os.path.abspath("") + "/geodata/rasters/Fr1000cfs.tif",
              raster_array=Froude, epsg=6418, geo_info=h_geo_info)


# ![img](https://raw.githubusercontent.com/sschwindt/hydroinformatics/main/docs/img/qgis-py-fr.png)

# (reproject-raster)=
# ### Reproject Raster 
# 
# The transformation (and reprojection) of a raster into a another coordinate system involves rotation, shifting, and shearing of pixels. If one of these operations is skipped, it can happen that the reprojected raster is squeezed, twisted, or placed somewhere else in the world. Therefore, the approach for the reprojection of a raster into another coordinate data system implies the following steps:
# 
# 1. Retrieve the source and target spatial reference systems (e.g., derive from a `gdal.Dataset` or an `EPSG` authority code).
# 1. Read the geo tansformation of the source dataset ( `gdal.Dataset.GetGeoTransform()`).
# 1. Derive the number of pixels and the spacing between pixels in the new (reprojected) dataset.
# 1. Instantiate the new (reprojected) dataset.
# 1. Project an image of the source dataset onto the new (reprojected) dataset (`gdal.ReprojectImage()`).
# 
# The spatial reference system can be derived from a dataset with the explanations in the [shapefile](geo-shp.html#prj-shp) section by writing a `get_srs` function. The following code block shows the `get_srs` function (uses the `osr` library from `osgeo` / `gdal` ), which is also integrated in the [flusstools package](https://flusstools.readthedocs.io/en/latest/geotools.html#module-flusstools.geotools.srs_mgmt).

# In[8]:


def get_srs(dataset):
    """
    Get the spatial reference of any gdal.Dataset
    :param dataset: osgeo.gdal.Dataset (raster)
    :output: osr.SpatialReference
    """
    sr = osr.SpatialReference()
    sr.ImportFromWkt(dataset.GetProjection())
    # auto-detect epsg
    auto_detect = sr.AutoIdentifyEPSG()
    if auto_detect is not 0:
        sr = sr.FindMatches()[0][0]  # Find matches returns list of tuple of SpatialReferences
        sr.AutoIdentifyEPSG()
    # assign input SpatialReference
    sr.ImportFromEPSG(int(sr.GetAuthorityCode(None)))
    return sr


# With the previously defined `open_raster` and `get_srs` functions we have all the necessary ingredients to accomplish the raster reprojection workflow in a `reproject_raster` function. An additional feature of the function is to ensure correct use of the `osr.CoordinateTransformation` method, which behaves differently under `gdal` 3.0 compared to previous `gdal` versions ([read on OSGeo's GitHub page](https://github.com/OSGeo/gdal/issues/1546)).

# In[9]:


def reproject_raster(source_dataset, source_srs, target_srs):
    """
    Reproject a raster dataset (preferably use through reproject function)
    :param source_dataset: osgeo.ogr.DataSource (instantiate with ogr.Open(SHP-FILE))
    :param source_srs: osgeo.osr.SpatialReference (instantiate with get_srs(source_dataset))
    :param target_srs: osgeo.osr.SpatialReference (instantiate with get_srs(DATASET-WITH-TARGET-PROJECTION))
    """
    # READ THE SOURCE GEO TRANSFORMATION (ORIGIN_X, PIXEL_WIDTH, 0, ORIGIN_Y, 0, PIXEL_HEIGHT)
    src_geo_transform = source_dataset.GetGeoTransform()
    
    # DERIVE PIXEL AND RASTER SIZE
    pixel_width = src_geo_transform[1]
    x_size = source_dataset.RasterXSize
    y_size = source_dataset.RasterYSize

    # ensure that TransformPoint (later) uses (x, y) instead of (y, x) with gdal version >= 3.0
    source_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    target_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    # get CoordinateTransformation
    coord_trans = osr.CoordinateTransformation(source_srs, target_srs)

    # get boundaries of reprojected (new) dataset
    (org_x, org_y, org_z) = coord_trans.TransformPoint(src_geo_transform[0], src_geo_transform[3])
    (max_x, min_y, new_z) = coord_trans.TransformPoint(src_geo_transform[0] + src_geo_transform[1] * x_size,
                                                       src_geo_transform[3] + src_geo_transform[5] * y_size,)

    # INSTANTIATE NEW (REPROJECTED) IN-MEMORY DATASET AS A FUNCTION OF THE RASTER SIZE
    mem_driver = gdal.GetDriverByName('MEM')
    tar_dataset = mem_driver.Create("",
                                    int((max_x - org_x) / pixel_width),
                                    int((org_y - min_y) / pixel_width),
                                    1, gdal.GDT_Float32)
    # create new GeoTransformation
    new_geo_transformation = (org_x, pixel_width, src_geo_transform[2],
                              org_y, src_geo_transform[4], -pixel_width)

    # assign the new GeoTransformation to the target dataset
    tar_dataset.SetGeoTransform(new_geo_transformation)
    tar_dataset.SetProjection(target_srs.ExportToWkt())

    # PROJECT THE SOURCE RASTER ONTO THE NEW REPROJECTED RASTER
    rep = gdal.ReprojectImage(source_dataset, tar_dataset,
                              source_srs.ExportToWkt(), target_srs.ExportToWkt(),
                              gdal.GRA_Bilinear)
    return tar_dataset


# Using the `reproject_raster` function in a *Python*  script requires a source dataset and another (orientation) dataset with the new coordinate system into which the source dataset will be projected. The following example shows how to project the *Froude* number raster created above into the `EPSG=3857` coordinate system for viewing it in *QGIS* on the *Google Satellite* base map ([recall basemaps in *QGIS* from the installation section](../get-started/geo.html#basemap)). As orientation data set we use `web_frame.tif`, which was created on the *Google Satellite* base map.
# 
# With the `get_srs` function that automatically detects the raster projection and spatial reference system we can use the `create_raster` function to reproject the above-created `Fr1000cfs.tif` raster (e.g., to `epsg=4326`).

# In[10]:


# load original and orientation rasters
source_file_name = r"" + os.path.abspath("") + "/geodata/rasters/Fr1000cfs.tif"
orientation_file_name = r"" + os.path.abspath("") + "/geodata/rasters/web_frame.tif"

src_dataset, src_band = open_raster(source_file_name)
ort_dataset, ort_band = open_raster(orientation_file_name)

src_srs = get_srs(src_dataset)
new_srs = get_srs(ort_dataset)

print("Source EPSG: " + str(src_srs.GetAuthorityCode(None)))
print("Target EPSG: " + str(new_srs.GetAuthorityCode(None)))

# flush orientation dataset
ort_dataset, ort_band = None, None

# create re-projected raster and save as GeoTIFF
reproj_dataset = reproject_raster(src_dataset, src_srs, new_srs)
reproj_file_name = r"" + os.path.abspath("") + "/geodata/rasters/Fr1000cfs_reproj.tif"
array_data = reproj_dataset.ReadAsArray()
new_epsg = int(new_srs.GetAuthorityCode(None))
geo_transformation = reproj_dataset.GetGeoTransform()
create_raster(reproj_file_name, raster_array=array_data, epsg=new_epsg, geo_info=geo_transformation)
reproj_dataset = None


# Plotted in *QGIS*, the reprojected *Froude* number raster looks like this:
# 
# ![img](https://raw.githubusercontent.com/sschwindt/hydroinformatics/main/docs/img/qgis-reproj-Froude.png)
# 
# The `reproject_raster` function is also available (slightly modified) in the [flusstools package](https://flusstools.readthedocs.io/en/latest/geotools.html#module-flusstools.geotools.srs_mgmt), where saving the new reprojected raster is embedded in the function (automatically appends the syllable `"_epsg[NO]"` to the original file name).
# 
# ```{note}
# To display multiple rasters with different coordinate systems on the same map in *QGIS*, the coordinate systems must be harmonized in most cases. *QGIS* has a dedicated function for adjusting raster coordinate systems: In *QGIS*, click on the `Raster` menu > `Projections` > `Warp (Reproject)...`. Select the raster(s) to reproject (i.e., the raster(s) to harmonize with project coordinate system). However, *Warp* may not perform all reprojection steps as desired and lead to wrong placements of the new raster. The *Warp* method is also available in *Python* through `gdal.Warp` ([read the docs](https://gdal.org/tutorials/warp_tut.html)): <br><br>`kwargs={'format': 'GTiff', 'geoloc': True}`<br>`gdal.Warp(TARGET_GEO_TIFF_FILE_NAME, SOURCE_GEO_TIFF_FILE_NAME, **kwargs)`
# ```
# 
# ```{important}
# The coordinate transformation fails when no transformation between the indicated source and target spatial reference system can be established (i.e., `gdal` does not know the transformation). This problem occurs often when old, regional coordinate systems are transformed to coordinate systems for web applications (e.g., `EPSG=3857`). Read more in the [*gdal* docs](https://gdal.org/tutorials/osr_api_tut.html#coordinate-transformation).
# ```

# (zonal)=
# ## Application Example with Zonal Statistics
# 
# In hydraulic and geospatial analyses, the question of statistical values of certain areas of one or more rasters often arises. For example, we may be interested in mean values and standard deviations in specific water body zones. *Zonal statistics* enable the delineation of an area of a raster by using a polygon shapefile.
# 
# The *RiverArchitect* dataset includes a slackwater zone and zonal statistics help to identify the mean water depth and flow velocity of slackwaters, which are a so-called morphological unit. 
# 
# ```{note}
# Instream morphological units aid to describe the geospatial organization of fluvial landforms, which play and important role in ecohydraulic analyses and river restoration. For example, pool units describe deep water zones with low flow velocity, riffle are typicall characterized by shallow water depths and high velocity, and slackwaters are shallow flow zones with low flow velocity (many juvenile fish love slackwaters). [Wyrick and Pasternack (2014)](https://www.sciencedirect.com/science/article/pii/S0169555X14000099) introduce the delineation of morphological units and an open-access summary can be found in the [Appendix Sect. 5 in Schwindt et al. (2020)](https://ars.els-cdn.com/content/image/1-s2.0-S235271101930281X-mmc1.pdf).
# ```
# 
# To analyze a visually apparent riffle unit, we need to draw a polygon within a new shapefile that delineates the slackwater. The following figures guide through the creation of a polygon shapefile and the delineation of the riffle with [*QGIS*](../get-started/geo.html#qgis). Start with opening *QGIS* and create a new project. Import the water depth and flow velocity rasters showing the slow and shallow water zone. Then:
# 
# ![img](https://raw.githubusercontent.com/sschwindt/hydroinformatics/main/docs/img/qgis-create-shp.png)
# ![img](https://raw.githubusercontent.com/sschwindt/hydroinformatics/main/docs/img/qgis-new-shp.png)
# ![img](https://raw.githubusercontent.com/sschwindt/hydroinformatics/main/docs/img/qgis-toggle-editing.png)
# ![img](https://raw.githubusercontent.com/sschwindt/hydroinformatics/main/docs/img/qgis-draw-polygon.png)
# 
# Finalize the drawing with a click on the Save Edits button (between Toggle Editing and Add Polygon). Just in case, the slackwater delineation polygon shapefile is also available at [the course repository](https://github.com/hydro-informatics/material-py-codes/raw/master/geo/slackwater-poly.zip) (during courses only).
# 
# ```{important}
# The new polygon is not saved as long as the edits are not save. That means: Regularly save edits when drawing features in *QGIS*.
# ```
# 
# Zonal statistics can be calculated using the `gdal` and `ogr` libraries, but this is a little bit cumbersome. The [*rasterio*](https://rasterio.readthedocs.io/en/latest/) (`conda install -c conda-forge rasterio`) library provides a much more convenient method to calculate zonal statistics with its `rasterstats.zonal_stats(SHP-FILE, RASTER, STATSTICS-TYPES)` method. With `zonal_stats`, we can easily obtain many statistical values of the water depth and flow velocity raster within the just drawn slackwater polygon.

# In[11]:


import rasterstats as rs
# make file names
h_file = r"" + os.getcwd() + "/geodata/river-architect/h001000.tif"
u_file = r"" + os.getcwd() + "/geodata/river-architect/u001000.tif"
zone = r"" + os.getcwd() + "/geodata/river-architect/slackw-poly.shp"

# get water depth stats in zone
h_stats = rs.zonal_stats(zone, h_file, stats=["min", "max", "median", "majority", "sum"])
# get flow velocity stats in zone - note the different stats assignment
u_stats = rs.zonal_stats(zone, u_file, stats="min max median majority sum")

print(h_stats)
print(u_stats)


# Recall that both rasters are in the U.S. customary unit system (i.e., feet and feet per second). More statistics can be calculated with `zonal_stats`: <br>
# `min`, `max`, `mean`, `count`, `sum`, `std`, `median`, `majority`, `minority`, `unique`, `range`, `nodata`, `percentile_<q>` (where `<q>` can be any float number between 0 and 100).
# 
# In addition, user-defined statistics can be added, where the [`numpy.ma`](https://numpy.org/doc/stable/reference/routines.ma.html#masked-arrays-arithmetics) module is particularly useful with its array handling capacities include transposing or specifying statistics along axis. For example, we can define a specific function to calculate standard deviation:

# In[12]:


def raster_std(raster_array):
       return np.ma.std(raster_array)


# Now, we can use the `raster_std` function in `zonal_stats`:

# In[13]:


u_stats = rs.zonal_stats(zone, u_file, stats="min max",
                         add_stats={"stdev": raster_std})
print(u_stats)


# (clip)=
# ## Clip Raster
# The above-introduced `rasterstats.zonal_stats` method works with *"Mini-Rasters"*, which represent clips of the input raster to the polygon shapefile used. The mini-rasters can be obtained by defining the optional keyword argument `raster_out=True`. In the case that we want to get the original raster clipped without and statistical operation, we can use a little trick by defining an additional statistics function that returns the original array:

# In[14]:


def original(raster_array):
       return raster_array


# With `raster_out=True` and the `original` function we can retrieve the clipped original raster as the following array types:
# * `mini_raster_array` - clipped and masked *numpy* array,
# * `mini_raster_affine` - transformation as an Affine object, and
# * `mini_raster_nodata` - NoData values.
# 
# The following code block illustrates the usage:

# In[15]:


import rasterstats as rs

h_file = r"" + os.getcwd() + "/geodata/river-architect/h001000.tif"
h_stats = rs.zonal_stats(zone, h_file, stats="count",
                         add_stats={"original": original},
                         raster_out=True)
print(h_stats[0].keys())
print(h_stats[0]["mini_raster_array"])


# ```{tip}
# Use the above shown methods to assign a projection and save the clipped array as *GeoTIFF* raster. The functions are implemented in flusstools (`flusstools.geotools.raster_mgmt.create_raster`(https://flusstools.readthedocs.io/en/latest/geotools.html#module-flusstools.geotools.raster_mgmt)).
# ```

# (terminal)=
# ## Slope / Aspect Maps and Built-in Command Line Scripts
# Hill slope maps are an important parameter in hydraulics, hydrology and ecology. The slope determines the flow direction of the water and it is also a criteria for delineating habitat of many species. `gdal` has a command line tool called `gdaldem` , which enables the creation of slope rasters based on a DEM (Digital Elevation Model) raster.
# The general use of the `gdaldem` in the command line is (arguments in brackets are optional): 

# ```
# gdaldem slope input_dem output_slope_map  [-p use percent slope (default=degrees)] [-s scale* (default=1)] [-alg ZevenbergenThorne] [-compute_edges] [-b Band (default=1)] [-of format] [-co "NAME=VALUE"]* [-q]
# ```

# To call the command line tool, we can use *Python*'s standard library `subprocess`. The following code block illustrates the usage of the `gdaldem` command line tool through [`subprocess.call`](https://docs.python.org/3/library/subprocess.html) to create a slope raster (in percent) from the *River Architect* sample data's `dem.tif`. `subprocess.call` returns `0` if the command execution was successful. Any other return value indicates an error.

# In[16]:


import subprocess, os

cmd_create_slope = 'gdaldem slope {0}/geodata/river-architect/dem.tif {0}/geodata/river-architect/slope-percent.tif -p'.format(os.path.abspath(''))
subprocess.call(cmd_create_slope)


# ![img](https://raw.githubusercontent.com/sschwindt/hydroinformatics/main/docs/img/qgis-slope.png)

# In addition to the absolute slope (i.e., inclination in degrees), or instead of the slope, it can be important to know the slope direction (e.g., inclination toward south, west, east, or north). A raster indicating the slope direction is called *Aspect* raster, where south corresponds to 0° (and 360°), west to 90°, north to 180°, and east to 270°. The ascpect raster can also be created with `gdaldem`:

# ```
# gdaldem aspect input_dem output_aspect_map [-trigonometric] [-zero_for_flat] [-alg ZevenbergenThorne] [-compute_edges] [-b Band (default=1)] [-of format] [-co "NAME=VALUE"]* [-q]
# ```

# To create an aspect raster of the *River Architect* sample data DEM run:

# In[17]:


cmd_create_aspect = 'gdaldem aspect {0}/geodata/river-architect/dem.tif {0}/geodata/river-architect/slope-aspect.tif'.format(os.path.abspath(''))
subprocess.call(cmd_create_aspect)


# ![img](https://raw.githubusercontent.com/sschwindt/hydroinformatics/main/docs/img/qgis-aspect.png)

# (leastcost)=
# ## Least Cost Path between Pixels (and another Way of Reprojection)
# 
# ### Ecohydraulic Background
# Least cost paths are important to plan efficient routes for navigation (e.g., in a car) and they can also be helpful in ecohydraulics. Let's take for a moment the position of a fish that after a flood with decreasing discharge wants to swim as fast as possible from the floodplain back into the main channel where there is enough water. In the figure below, point 1 shows the starting point on the floodplain and point 2 the destination in the main channel. The reddish background represents the previously produced slope raster (slope-percent.tif) and the water depth at normal runoff is colored in blue.

# ![img](https://raw.githubusercontent.com/sschwindt/hydroinformatics/main/docs/img/qgis-slope-pts.png)

# Naturally the path of least cost in this case corresponds to the path of the steepest monotonously downward facing slope and it can be assumed that a fish is able to find it.
# 
# ```{note}
# In many rivers fish face the daily challenge of escaping from the deadly trap of lateral depressions. The reason for this is that many hydroelectric power plants cause abrupt fluctuations in discharge due to fluctuations in energy demand and production (so-called hydro-peaking). As a result, there is a so-called stranding risk for fish in many regulated rivers. The following figure illustrates stranding risk zones as a function of discharge (in cubic feet per second) at the lower Yuba River (California, USA).
# ```
# 
# ![img](https://raw.githubusercontent.com/sschwindt/hydroinformatics/main/docs/img/ra-stranding.png)
# 
# *Image source: [The River Architect Wiki / Kenneth Larrieu](https://riverarchitect.github.io/RA_wiki/StrandingRisk)*

# (lc-fun)=
# ### Functions and Libraries Involved 
# 
# The `skimage` (`scikit-image`) library (see [*Other packages* on the *Open source libraries* page](geo-pckg.html#others)) provides with [`skimage.graph.route_through_array`](https://scikit-image.org/docs/0.13.x/api/skimage.graph.html) a smart method to calculate a least cost path by summing up pixel-wise connections from point 1 to point 2. Here is how it works: Assume a *numpy* array (e.g., with random slope values) that looks like this:

# In[18]:


slope_image = np.random.randint(100, size=(3, 5))
slope_image


# To find the fastest way from array index `[0][0]` (top left point `A = (0, 0)`) to array index `[2][4]` (bottom right point `B = (2, 4)`) we can use `route_through_array` to get a *list* (`least_cost_path_indices`) with the array coordinates of the path to go and the costs (`weight`) involved (sum of all pixels of the least cost path):

# In[19]:


from skimage.graph import route_through_array

point_A = (0, 0)
point_B = (2, 4)
least_cost_path_indices, weight = route_through_array(slope_image, point_A, point_B)
least_cost_path_indices, weight


# To integrate the least cost path list into an array that we can *rasterize* (`create_raster`) afterwards, we can paste `least_cost_path_indices` into a *numpy* zeros array of the original slope raster (image) as a transposed list.

# In[20]:


least_cost_path_indices = np.array(least_cost_path_indices).T
least_cost_path_array = np.zeros_like(slope_image)
least_cost_path_array[least_cost_path_indices[0], least_cost_path_indices[1]] = 1
least_cost_path_array


# In practice, the slope raster is georeferenced, and therefore, we have to use some pixel coordinates, relative to the coordinate system origin. For this purpose we need two more functions:
# 
# * One function to calculate the pixel-index related offset that we will name `coords2offset`: The `coords2offset` returns the x-y shift in the form of "number of pixels" (two *integer*s, one for *x* and one for *y* shift). 
# * The [above-defined `get_srs`](#reproject) function.
# 
# The `coords2offset` function looks like this:

# In[21]:


def coords2offset(geo_transform, x_coord, y_coord):
    """
    Returns x-y pixel offset
    :param geo_transform: osgeo.gdal.Dataset.GetGeoTransform() object
    :param x_coord: FLOAT of x-coordinate
    :param y_coord: FLOAT of y-coordinate
    :return: offset_x, offset_y (both integer of pixel numbers)
    """
    origin_x = geo_transform[0]
    origin_y = geo_transform[3]
    pixel_width = geo_transform[1]
    pixel_height = geo_transform[5]
    offset_x = int((x_coord - origin_x) / pixel_width)
    offset_y = int((y_coord - origin_y) / pixel_height)
    return offset_x, offset_y


# ```{tip}
# The `coords2offset` function is also available in the {{ ft_url }} package in robust raise-exception notation:  [*flusstools.geotools/dataset_mgmt*](https://flusstools.readthedocs.io/en/latest/geotools.html#module-flusstools.geotools.dataset_mgmt).
# ```

# Now we can use `coords2offset` to convert a raster array (e.g., produced with the above-defined `raster2array` function) into an array that can be used with `route_through_array`:
# 
# 1. Use the raster's `geo_transform` (`gdal.Dataset.GetGeoTransform = (origin_x, pixel_width, 0, origin_y, 0, pixel_height)`) and the start and end point coordinates (i.e, `start_coord` of point A/1 and `stop_coord` of point B/2) in `coords2offset` to get their pixel indices (`start_index_x`, `start_index_y`, `stop_index_x`, and `stop_index_y`) in the raster array.
# 1. Replace `np.nan` values in the raster array with values that are higher than the maximum of the array - do not use zeros, because we want to exclude these pixels from the least cost path by assigning very high costs).
# 1. Use `route_through_array` as above explained with the optional arguments `geometric=True` (use the [*MCP_Geometric* class](https://scikit-image.org/docs/0.13.x/api/skimage.graph.html#skimage.graph.MCP_Geometric) rather than [*MCP_base*](https://scikit-image.org/docs/0.13.x/api/skimage.graph.html#skimage.graph.MCP) to calculate costs) and `fully_connected=True` (enables using diagonal pixels as direct neighbors).
# 1. Integrate the least cost path list (`index_path`) into a *numpy* zeros array (child of `raster_array`), as above explained, and return the `path_array`.

# In[22]:


def create_path_array(raster_array, geo_transform, start_coord, stop_coord):
    # transform coordinates to array index
    start_index_x, start_index_y = coords2offset(geo_transform, start_coord[0], start_coord[1])
    stop_index_x, stop_index_y = coords2offset(geo_transform, stop_coord[0], stop_coord[1])

    # replace np.nan with max raised by an order of magnitude to exclude pixels from least cost
    raster_array[np.isnan(raster_array)] = np.nanmax(raster_array) * 10

    # create path and costs
    index_path, cost = route_through_array(raster_array, (start_index_y, start_index_x),
                                               (stop_index_y, stop_index_x),
                                               geometric=True, fully_connected=True)


    index_path = np.array(index_path).T
    path_array = np.zeros_like(raster_array)
    path_array[index_path[0], index_path[1]] = 1
    return path_array


# (lc-app)=
# ### Application
# 
# Recall, we defined the following functions (all are available in the {{ ft_url }} package) that we can use now for the calculation of the least cost path to get from point 1 to point 2 in the `slope-percent.tif` raster:
# 
# * `raster2array` 
# * `create_path_array`
# * `get_srs`
# * `create_raster`
# 
# The below code block uses these functions as follows:
# 
# 1. Define input (`slope-percent.tif`) and output (`least_cost.tif`) raster directories.
# 1. Define the coorindates of points 1 and 2 as *tuple*s (x, y) in the *EPSG:6418* projection.
# 1. Load the input raster(`src_raster`), its band as array (`raster_array`), and geotransformation (`geo_transform`) with the `raster2array` function.
# 1. Get the least cost path indicated with ones in a zero-s (on-off) array (`path_array`) with the `create_path_array` function.
# 1. Get the `osgeo.osr.SpatialReference` of the input raster (`src_raster = osgeo.gdal.Dataset(slope-percent.tif)`).
# 1. Create the least cost path raster *GeoTIFF* with the `create_raster` function as `gdal.GDT_Byte` band.

# In[23]:


from skimage.graph import route_through_array

# define raster input and out names
in_raster_name = r"" + os.path.abspath('') + "/geodata/river-architect/slope-percent.tif"
out_raster_name = r"" + os.path.abspath('') + "/geodata/river-architect/least_cost.tif"
# define coordinates of points 1 and 2 (in EPSG:6418)
point_1_coord = (6749261.94092826917767525, 2206970.35179582564160228)  
point_2_coord = (6749016.82820663042366505, 2207050.61491037486121058)

# get source raster (osgeo.gdal.Dataset), the raster as nd.array, and the geotransformation tuple
src_raster, raster_array, geo_transform = raster2array(in_raster_name)
# get the zeros-like array with least cost pixels = 1
path_array = create_path_array(raster_array, geo_transform, point_1_coord, point_2_coord)
# get the spatial reference system of the input raster (slope-percent.tif)
src_srs = get_srs(src_raster)
# project the least cost path_array into a Byte (only zeros and ones) raster
create_raster(out_raster_name, path_array, epsg=int(src_srs.GetAuthorityCode(None)),
              rdtype=gdal.GDT_Byte, geo_info=geo_transform)


# ![img](https://raw.githubusercontent.com/sschwindt/hydroinformatics/main/docs/img/qgis-least-cost.png)

# Legitimately, you may wonder whether it was better to represent a least cost path as a line. That is correct, of course. This operation is a conversion of a raster into a line shapefile, which is explained on the [conversion page](geo-convert.html#raster2line). Curious readers can also directly use the `raster2line` function of the {{ ft_url }} package (the function is part of the [*flusstools.geotools/dataset_mgmt.py*](https://flusstools.readthedocs.io/en/latest/geotools.html#module-flusstools.geotools.dataset_mgmt) script).

# ```{admonition} Exercise
# Get more familiar with raster handling in the [geospatial ecohydraulics](../exercises/ex-geco) exercise.
# ```

# In[ ]:




