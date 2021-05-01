# The Commercial arcpy Library

Summary: Geospatial analyses with ESRI's commercial ArcGIS software and arcpy package.

## Introduction

*ESRI*'s *ArcGIS Pro* software comes with its own *conda* environment that enables working with the commercial `arcpy` library. `arcpy` is accessible either directly in `ArcGIS Pro` or by using *ESRI*'s *conda* environment, which can be managed through *ArcGIS Pro*. Since `arcpy` is tied to the use of a commercial environment, it can only be accessed in *jupyter* notebooks directly hosted at [esri.com](https://notebooks.esri.com/) (however, these will not work with the examples on this page). This page explains the basic usage of `arcpy` in external [*IDE*](../get-started/ide.html#ide)s (e.g. *PyCharm*), the integration of licenses, and basic functionality of `arcpy`.

```{admonition} Requirements
Make sure to understand the difference between rasters and shapefiles as explained in the [introduction to geospatial data](geospatial-data) section.
```

```{note}
The development of **ArcMap** with its *Python2* executable **is discontinued**. For this reason only the usage of *ArcGIS Pro* with its *Python3* environment is explained here.
```

```{admonition} Linux Users
:class: warning
ArcGIS Pro and the wrappers that constitute the `arcpy` library are **Windows only** applications. At the time of writing this introduction *ArcGIS Pro* and `arcpy` cannot be used on *Linux* or *macOS* platforms.
```

## Background

***Why can working with `arcpy` in *Python* still be a powerful tool even though there are many license and platform restrictions?***

If you are working for a company with engineering service, it is likely that the company uses the *ArcGIS* software because of its popularity and commercial support service. In this case a company (or research institution) covers the license fees and it is equally likely that a *Windows* operating system is used for similar reasons. Among the popular functionalities of *ArcGIS* software are *Raster Calculator*, *Shapefile Feature* manager or tools for statistical analysis of geo-databases. Thanks to `arcpy`, such popular *ArcGIS* tools can be embedded in *Python* scripts, thus enabling workflows to be automated and efficiency to be significantly increased.

This page shows the basics for manipulating raster and shapefile data in *Python* with `arcpy`. There are many more methods implemented in `arcpy` and only the fundamentals are explained here.

## Use `arcpy` in External *IDE*s

### Setup Interpreter

The *Python* installation section explains [how to set up *PyCharm IDE*](](../python-basics/pyinstall.html#ide-setup) with a *conda* environment. To create a new *conda* environment in *PyCharm* with *ESRI*'s *conda* environment, the ***Location*** must be defined differently (see the [original screenshot](https://raw.githubusercontent.com/sschwindt/hydroinformatics/main/docs/img/pyc-prj-setup.png)):

* If *ArcGIS* Pro was globally installed by the system administrator, use: `%PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\propy`
* If *ArcGIS* Pro was installed for individual users, use: `%LOCALAPPDATA%\Programs\ArcGIS\Pro\bin\Python\Scripts\propy`

It may occur that it is not necessary to add the `propy` directory. Moreover, find the `conda.exe` or `python.exe` in the above directories and define it in the field ***Conda executable***. Finalize the creation of the new environment with a click on *Create*.

To install more packages follow the [descriptions povided by *esri*](https://developers.arcgis.com/python/guide/install-and-set-up/#Step-1:-Get-Conda).

```{tip}
If you are struggling with the above instructions, have a look at the [developer's docs on running stand-alone scripts](https://pro.arcgis.com/en/pro-app/arcpy/get-started/using-conda-with-arcgis-pro.htm) (look for instructions using `propy` rather than `python27`).
```

### Import arcpy and its Modules
`arcpy` comes with own classes for geospatial data objects (e.g., `arcpy.Raster` for gridded data) and modules for mapping (`arcpy.mp`), emulation of the *Spatial Analyst* (`arcpy.sa`), or accessing data (`arcpy.da`). A full list is provided on the [developer's website](https://pro.arcgis.com/en/pro-app/arcpy/get-started/importing-arcpy.htm). This page features code blocks using `arcpy` and `arcpy.sa`, where *Spatial Analyst* objects are imported using `*` to enable the direct access to, for example, `Con()` (instead of `arcpy.sa.Con()`), which corresponds to `arcpy`'s conditional statement for rasters.

import arcpy
from arcpy.sa import *

### Setup arcpy Workspace

Geospatial calculations may produce many side products, which can be heavy in size. To better control which data is generated by `arcpy` and where, it is a good idea to define a workspace for each arcpy script with:

arcpy.env.workspace = "C:\\workspace\\"  # or use os.path.dirname(__file__) to go to the script directorys

```{important}
Avoid blanks in the workspace directory.
```

It can also be useful to enable overwriting of already existing files with the same name because of the file size. This behavior may or may not be desired and can be controlled as follows.

arcpy.gp.overwriteOutput = True   # enable overwriting
arcpy.gp.overwriteOutput = False  # disable overwriting

### Set Spatial Extent

Geospatial datasets may have large extents without any data written to large parts. Processing void data cells may lead to unnecessarily long calculation time. Therefore, it is advisable to limit the calculation extent with:

arcpy.env.extent = "MAXOF"  # uses the combined extent of all input datasets
arcpy.env.extent = "MINOF"  # uses only the overlap of all input datasets
arcpy.env.extent = arcpy.Extent(arcpy.Raster("base.tif"))  # uses the controlled extent of a raster
arcpy.env.extent = "Xmin YMin XMax Ymax"  # imposes user-defined minimum and maximum coordinates

(licenses)=
### Checkout Licenses

Many `arcpy` methods need licenses such as *Spatial Analyst* or *3D*. In stand-alone scripts, licenses can be activate (*checked out*) with `arcpy.CheckOutExtension('NAME')` and deactivated (*checked in*) with `arcpy.CheckInExtension('NAME')`. In light of the object orientation, `arcpy` operations should be embedded in functions or methods of classes. Therefore, it is recommended to wrap functions or methods using `arcpy` with [decorators](../python-basics/pyfun.html#wrappers) that activate necessary licenses. The following code block provides an wrapper to activate a *Spatial Analyst* license for a function.

def spatial_license(func):
    def wrapper(*args, **kwargs):
        arcpy.CheckOutExtension('Spatial')
        func(*args, **kwargs)
        arcpy.CheckInExtension('Spatial')
    return wrapper

(arcpy-errors)=
### Track Errors

The [Errors, Logging and Debugging](../python-basics/pyerror) section provides useful instructions for troubleshooting errors in code or code usage. To identify problems in object-oriented `arcpy` scripts, an additional wrapper function is recommended, which writes `arcpy` errors to a log file (`logger`). The `logger.*(MESSAGE)` expressions can also be replaced with `print(MESSAGE)`.

def err_info(func):
    def wrapper(*args, **kwargs):
        arcpy.gp.overwriteOutput = True
        logger = logging.getLogger("logfile")
        try:
            func(*args, **kwargs)
        except arcpy.ExecuteError:
            logger.info(arcpy.GetMessages(2))
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            logger.info(e.args[0])
            arcpy.AddError(e.args[0])
        except:
            logger.info(arcpy.GetMessages())
    return wrapper

## Spatial Analyst & Raster Operations

### Basics

`arcpy` provides different options to load geospatial [rasters](https://pro.arcgis.com/en/pro-app/arcpy/classes/raster-object.htm) (gridded data), which may have different formats such as *Esri Grid* (no ending, the raster is a folder with other files), [*TIF*](http://download.osgeo.org/geotiff/spec/), *DAT*, and many more. The following script loads a flow depth Grid raster `h` and a flow velocity Grid raster `u`:

h = arcpy.Raster("geodata/input/rasters/h")
u = arcpy.Raster("geodata/input/rasters/u")

The [Froude number](https://en.wikipedia.org/wiki/Froude_number) can be calculated pixel by pixel from the flow depth and velocity and the gravity constant *g*=9.81m/s. The following script calculates the Froude number for all pixels where the flow depth is at least 0.1 m. The raster comparison is achieved through the *Spatial Analyst*'s `Con(if_condition, then, else)` conditional statement. The two rasters (`u` and `h`) are passed as `arcpy.sa.Float()` objects to ensure that the script uses the correct pixel data type. 

froude = Con(Float(h) > 0.1, Float(u) / SquareRoot(Float(h) * Float(9.81)))

Better than the 0.1-meter criterion is to calculate the Froude number everywhere where the flow depth and the velocity have a numerical value. `arcpy.sa.IsNull()` evaluates where pixels are non-numeric. However, we are interested in the opposite (i.e., pixels that are not non-numeric), which we get through the `~` (not) sign. The below functionalized calculation of the Froude number takes advantage of the possibility to nest multiple `Con()` expressions to check both rasters (`u` and `h`) for numeric pixels.
In addition, we need a Spatial Analyst license to run this script. Therefore, it makes sense to rewrite the above code block into a function that uses the `spatial_license` wrapper function from the above [Checkout Licenses](#licenses) section. To make the code robust, we also add the [above-defined `err_info`](arcpy-errors) wrapper function. 

@err_info
@spatial_license
def calculate_froude(h, u):
    return Con(~IsNull(h), Con(~IsNull(u), Float(u) / SquareRoot(Float(h) * Float(9.81))))

froude = calculate_froude(h, u)

Find out more about *Raster Calculator* and *Map Algebra* on the [developer's website (esri)](https://pro.arcgis.com/en/pro-app/tool-reference/image-analyst/raster-calculator.htm).

```{tip}
The functions provided with *Raster Calculator* can also be performed with the open access libraries `gdal` and `numpy`. All you need to do is:

1. Read [raster as array](geo-raster.html#createarray).

2. Use [`numpy`](](../python-basics/pynum.html#array-matrix-operations) and/or [`pandas`](../python-basics/pynum.html#pandas) to run typical *Raster Calculator* operations and many (many many) more on the array.

3. [Write the array back to a raster](geo-raster.html#create).
```

### Cell Statistics

The evaluation of numerical model data often involves calculating statistical values (e.g., minimum or maximum) of one or more rasters. The comparison of several similar rasters is useful, for example, if the same parameter was calculated with two different models or at different dates (e.g., to assess the morphodynamic evolution of rivers). `arcpy.sa.CellStatistics([Raster1, Raster2, ... RasterN], TYPE, ...)` enables such statistical evaluations. The following code blocks illustrates the comparison of flow velocities calculated with two different hydrodynamic numerical models through the calculation of the `MEAN` (average) and standard deviation (`STD`).

u_basement = arcpy.Raster("geodata/bm/velocity.tif")
u_tuflow = arcpy.Raster("geodata/tf/velocity.dat")

u_mean = CellStatistics([u_basement, u_tuflow], "MEAN")
u_stdv = CellStatistics([u_basement, u_tuflow], "STD")

Read more options statistics types and handling non-numeric data on the [developer's website (esri)](https://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/cell-statistics.htm).

```{tip}
An open access alternative to `arcpy`'s `CellStatistics` is the [`rasterstats` library](geo-raster.html#zonal) (usage: `rasterstats.zonal_stats(zone, raster_file_name, stats=['min', 'max', 'median', 'majority', 'sum', '...many more...'])`). 
```

## Shapefile Operations

The geospatial [shapefile](https://en.wikipedia.org/wiki/Shapefile) vector format is an *Esri* invention. No wonder that `arcpy` is good at handling this vector data format. In hydraulic engineering, however, we usually create (draw) shapefiles manually either directly with *ArcGIS* or its open-source competitor [*QGIS*](https://www.qgis.org/) to delineate, for example, particular flow regions. Examples can be found [in the BASEMENT tutorial](../numerics/basement) simulation (explore the creation of elevation point, boundary polygon, and breakline polyline shapefiles). In codes, the processing of shapefiles only becomes important in the analysis of the output of numerical models (e.g., to classify morphological unit features, exactly calculate patch areas, or automatically place reinforcements in construction plans). At this stage, raster data (output of numerical models) must first be converted into shapefiles. This is why this tutorial starts with the conversion of raster data to shapefiles along with the illustration of other functions such as calculating patch area and accessing shapefile attribute tables.

Rasters can be converted to polygon and other shapefile types (e.g., point). The following example features the conversion of a raster to a polygon shapefile. It uses an integer raster of all pixels where the flow depth and velocity are smaller than 1.4 m and 0.15 m/s, respectively. Such shallow and slow-flow regions are called *slackwater* (according to [Wyrick & Pasternack 2014](https://doi.org/10.1016/j.geomorph.2013.12.040)). Because slackwater is designated preferred habitat of some aquatic species, we are wondering now how much slackwater area the numerical model predicts in the simulated river section. For this purpose, we convert the slackwater raster to a shapefile and calculate the surface area of the shapefile with the following `arcpy` methods:

* Convert the raster to a shapefile with [`arcpy.RasterToPolygon_conversion()`](https://pro.arcgis.com/en/pro-app/tool-reference/conversion/raster-to-polygon.htm) with arguments:
    - `in_raster` is an `arcpy.Raster()` object of **integer** values (using a `Float` raster results in an error!).
    - `out_polygon_features` is a *string* of the output file name and directory.
    - `simplify` is an optional *string* that can be either `"NO_SIMPLIFY"` to force exact drawing of polygon boundaries along pixel boarder, or `"SIMPLIFY"` to enable polygon boundaries crossing pixels.
* Add a new field to the new polygon shapefile with [`arcpy.AddField_management()`](https://pro.arcgis.com/en/pro-app/tool-reference/data-management/add-field.htm) with arguments:
    - `field_name` can be any *string* without blanks.
    - `field_type` is a *string* defining if the field is numeric (e.g., `"FLOAT"` or `"LONG"` for *integer*), date/time (`"DATE"`), `"TEXT"`, or `"RASTER"`.
    - `field_precision` is an (optional) *integer* (*Long*) defining the number of digits that can be stored in the new field.
    - More optional arguments can be set to define the number of decimals or characters, an alternative field name, enable `NULL`, a field domain, or if a field is required.
* Calculate patch area with [`arcpy.CalculateGeometryAttributes_management()`](https://pro.arcgis.com/en/pro-app/tool-reference/data-management/calculate-geometry-attributes.htm) with arguments:
    - `in_features` is a *string* defining the directory and name of a feature layer.
    - `geometry_property` is a nested list of `[[Target-field-name, Property], [Another-target-field-name, Another-property], ...]` for calculating geometric properties such as `"AREA"`, `"HOLE_COUNT"`, or `"PART_COUNT"` (and many more).
    - `area_unit` can be `"SQUARE_METERS"` or `"SQUARE_KILOMETERS"` (and many other options for U.S. customary units).
    - More optional arguments can be set to define length units (for perimeter assessments), or a coordinate system and format.
    
The below code block additionally features the application of these methods and also illustrates how the area value can be read row-by-row from the attribute table of a shapefile with `arcpy.da.UpdateCursor(shapefile-name, field-name)`.

# create a slackwater raster that is arcpy.sa.Int(1) where h and u criteria are true and NULL elsewhere
slackwater = Con(Float(h) <= 1.4 & Float(u) <= 0.15, Int(1))


# define directory and name of the new shapefile
new_shp_file = "geodata/shapefiles/slackwater.shp"
# convert slackwater raster to polygon shapefile
arcpy.RasterToPolygon_conversion(in_raster=slackwater, out_polygon_features=new_shp_file, simplify="NO_SIMPLIFY")
# add a new field to the new shapefile's attribute table (name)
arcpy.AddField_management(shp_name, field_name="F_AREA", field_type="FLOAT", field_precision=9)
# calculate area of all polygons in attribute table
area_unit="SQUARE_METERS"
arcpy.CalculateGeometryAttributes_management(in_features=shp_name, geometry_property=[["F_AREA", "AREA"]], area_unit=area_unit)

with arcpy.da.UpdateCursor(shp_name, "F_AREA") as cursor:
    for row in cursor:
        try:
            area += float(row[0]) 
        except ValueError:
            print("WARNING: Patch with invalid area value (%s)." % str(row))

print("Sum of all patches = {0} {1}".format(str(area), area_unit))

```{warning}
Never calculate areas directly from rasters by multiplying the number (quantity) of pixels that fulfill a certain criterion with the pixel size (e.g., 1mx1m). This calculation often fails in practice because of erroneous internal assignments of cell sizes, which can hardly be controlled in a robust manner (in particular when switching between U.S. customary and S.I. units).
```

```{tip}
Shapefile handling, deriving geometric properties and many more operations can also be performed with the `ogr` library, which comes along with `gdal`. Read more in the [shapefile handling](geo-shp) section.
```