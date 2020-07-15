---
title: Convert Raster to Vector datasets and Vice Versa
tags: [python, gdal, pandas, geo, geospatial, shapefile, raster]
keywords: geo-python gdal QGIS
sidebar: mydoc_sidebar
permalink: geo-convert.html
folder: geopy
---


The goal of this page is to guide to an understanding of conversions from raster and to vector data formats and vice versa.

{% include requirements.html content="Make sure to understand [gridded raster data](geo-raster.html) and [vector data](geo-shp.html) data handling before reading this section.<br>Recall the [`open_raster`](geo-raster.html#open) and [`create_shp`](geo-shp.html#create) functions.<br>Read through the creation of the [*least cost path*](geo-raster.html#leastcost) raster dataset." %}
{% include tip.html content="The core functions used in this e-book are introduced with the raster and vector data handling explanations and additionally implemented in the [`geo_utils`](https://github.com/hydro-informatics/geo-utils) package." %}
{% include tip.html content="Download sample raster datasets from [*River Architect*](https://github.com/RiverArchitect/SampleData/archive/master.zip). This page uses *GeoTIFF* raster data located in [`RiverArchitect/SampleData/01_Conditions/2100_sample/`](https://github.com/RiverArchitect/SampleData/tree/master/01_Conditions/2100_sample)." %}

## Vectorize

### Raster to line {#raster2line}
In this section, we convert the [*least cost path*](geo-raster.html#leastcost) raster dataset (`least_cost.tif`) into a (poly) line shapefile. For this purpose we first write a function called `offset2coords`, which represents the inverse of the [`coords2offset`](geo-raster.html#lc-fun) function, to convert x/y offset (in pixel numbers) to coordinates of a geospatial dataset's geo-transformation:


```python
def offset2coords(geo_transform, offset_x, offset_y):
    # get origin and pixel dimensions from geo_transform (osgeo.gdal.Dataset.GetGeoTransform() object)
    origin_x = geo_transform[0]
    origin_y = geo_transform[3]
    pixel_width = geo_transform[1]
    pixel_height = geo_transform[5]
    
    # calculate x and y coordinates
    coord_x = origin_x + pixel_width * (offset_x + 0.5)
    coord_y = origin_y + pixel_height * (offset_y + 0.5)

    # return x and y coordinates
    return coord_x, coord_y
```

{% include note.html content="The offset is added 0.5 pixels in both x and y directions to meet the center of the pixel rather than the top left pixel corner." %}

Next we can write the core function to convert a raster dataset to a line shapefile. This function named `raster2line`:
1. Opens a `raster`, its band as `array` and `geo_transform` (geo-transformation) defined with the `raster_file_name` argument and using the [`open_raster`](geo-raster.html#open) function.
1. Calculates the maximum distance (`max_distance`) between two pixels that are considered *connect-able*, based on the hypothesis that the pixel height *&Delta;y* and width *&Delta;x* are the same:
    {% include image.html file="pixel2line-width-illu.png" alt="dpix" max-width="500" %}
1. Gets the `trajectory` of pixels that have a user parameter-defined `pixel_value` (e.g., `1` to trace 1-pixels in the binary `least_cost.tif`) and throws an error if the trajectory is empty (i.e., `np.count_nonzero(trajectory) is 0`). 
1. Uses the above define `offset2coords` function to append point coordinates to a `points` list.
1. Creates a `multi_line` object (instance of `ogr.Geometry(ogr.wkbMultiLineString)`), which represents the (void) final least cost path.
1. Iterates through all possible combinations of points (excluding combinations of points with themselves) with [`itertools.combinations(iterable, r=number-of-combinations=2`](https://docs.python.org/3/library/itertools.html)).
    * Points are stored in the `points` list.
    * `point1` and `point2` are required to get the distance between pairs of points.
    * If the `distance` between the point is smaller than `max_distance`, the function creates a line object from the two points and appends it to the `multi_line`.
1. Creates a new shapefile (named `out_shp_fn`) using the [`create_shp`](geo-shp.html#create) function (with integrated shapefile name length verification as per the [`geo_utils`](https://github.com/hydro-informatics/geo-utils) package).
1. Adds the `multi_line` object as new feature to the shapefile (follows the descriptions on the [shapefile page](geo-shp.html#line-create)).
1. Creates a `.prj` projection file (recall descriptions on the [shapefile page](geo-shp.html#prj-shp)) using the spatial reference system of the input `raster` with the [`get_srs`](geo-raster.html##lc-fun) function.
The `raster2line` function is also implemented in the [`geo_utils/geo_tools.py`](https://github.com/hydro-informatics/geo-utils/blob/master/geo_utils/geo_tools.py) script.


```python
def raster2line(raster_file_name, out_shp_fn, pixel_value):
    """
    Convert a raster to a line shapefile, where pixel_value determines line start and end points
    :param raster_file_name: STR of input raster file name, including directory; must end on ".tif"
    :param out_shp_fn: STR of target shapefile name, including directory; must end on ".shp"
    :param pixel_value: INT/FLOAT of a pixel value
    :return: None (writes new shapefile).
    """

    # calculate max. distance between points
    # ensures correct neighbourhoods for start and end pts of lines
    raster, array, geo_transform = raster2array(raster_file_name)
    pixel_width = geo_transform[1]
    max_distance = np.ceil(np.sqrt(2 * pixel_width**2))

    # extract pixels with the user-defined pixel value from the raster array
    trajectory = np.where(array == pixel_value)
    if np.count_nonzero(trajectory) is 0:
        print("ERROR: The defined pixel_value (%s) does not occur in the raster band." % str(pixel_value))
        return None

    # convert pixel offset to coordinates and append to nested list of points
    points = []
    count = 0
    for offset_y in trajectory[0]:
        offset_x = trajectory[1][count]
        points.append(offset2coords(geo_transform, offset_x, offset_y))
        count += 1

    # create multiline (write points dictionary to line geometry (wkbMultiLineString)
    multi_line = ogr.Geometry(ogr.wkbMultiLineString)
    for i in itertools.combinations(points, 2):
        point1 = ogr.Geometry(ogr.wkbPoint)
        point1.AddPoint(i[0][0], i[0][1])
        point2 = ogr.Geometry(ogr.wkbPoint)
        point2.AddPoint(i[1][0], i[1][1])

        distance = point1.Distance(point2)
        if distance < max_distance:
            line = ogr.Geometry(ogr.wkbLineString)
            line.AddPoint(i[0][0], i[0][1])
            line.AddPoint(i[1][0], i[1][1])
            multi_line.AddGeometry(line)

    # write multiline (wkbMultiLineString2shp) to shapefile
    new_shp = create_shp(out_shp_fn, layer_name="raster_pts", layer_type="line")
    lyr = new_shp.GetLayer()
    feature_def = lyr.GetLayerDefn()
    new_line_feat = ogr.Feature(feature_def)
    new_line_feat.SetGeometry(multi_line)
    lyr.CreateFeature(new_line_feat)

    # create projection file
    srs = get_srs(raster)
    make_prj(out_shp_fn, int(srs.GetAuthorityCode(None)))
    print("Success: Wrote %s" % str(out_shp_fn))
```

Now we can use the `raster2line` function to convert the least cost path from pixel (raster) format to line format:


```python
source_raster_fn = r"" +  os.path.abspath('') + "/geodata/river-architect/least_cost.tif"
target_shp_fn = r"" + os.path.abspath('') + "/geodata/river-architect/least_cost.shp"
pixel_value = 1
raster2line(source_raster_fn, target_shp_fn, pixel_value)
```

{% include image.html file="qgis-least-cost-line.png" alt="aspect" caption="The newly created least cost path least_cost.shp line shapefile plotted in QGIS." %}

{% include challenge.html content="There is a small fault in the `least_cost` line. Can you find the fault? What can be done to fix the fault?" %}

{% include note.html content="Network routing is the core specialty of the [`NetworkX` package (see *Open source libraries*)](geo-pckg.html#other). Read more about network analyses in [Michael Diener's *GitHub* pages](https://github.com/mdiener21/python-geospatial-analysis-cookbook/tree/master/ch08)." %}

### Raster to polygon {#raster2polygon}

`gdal` comes with the powerful `Polygonize` functionality for the easy conversion of a raster dataset to a polygon shapefile. While `gdal.Polygonize` enables writing a simple `raster2polygon` function, it has a drawback, which is that it can only handle integer values and it merely randomly attributes `FID` values by default. Because the `FID` values are not meaningful, we can implement the following `float2int` function to preserve the original value range (uses the [`raster2array`](geo-raster.html#createarray) and [`create_raster`](geo-raster.html#create) functions explained on the raster page):


```python
def float2int(raster_file_name, band_number=1):
    """
    :param raster_file_name: STR of target file name, including directory; must end on ".tif"
    :param band_number: INT of the raster band number to open (default: 1)
    :output: new_raster_file_name (STR)
    """
    # use raster2array function to get raster, np.array and the geo transformation
    raster, array, geo_transform = raster2array(raster_file_name, band_number=band_number)
    
    # convert np.array to integers
    try:
        array = array.astype(int)
    except ValueError:
        print("ERROR: Invalid raster pixel values.")
        return raster_file_name
    
    # get spatial reference system
    src_srs = get_srs(raster)
    
    # create integer raster    
    new_name = raster_file_name.split(".tif")[0] + "_int.tif"
    create_raster(new_name, array, epsg=int(src_srs.GetAuthorityCode(None)),
                  rdtype=gdal.GDT_Int32, geo_info=geo_transform)
    # return name of integer raster
    return new_name
```

The following `raster2polygon` function:
1. Uses the `float2int` function to ensure that any raster `file_name` provided is converted to purely integer values.
1. Creates a new shapefile (named `out_shp_fn`) using the [`create_shp`](geo-shp.html#create) function (with integrated shapefile name length verification as per the [`geo_utils`](https://github.com/hydro-informatics/geo-utils) package).
1. Adds a new `ogr.OFTInteger` field (recall [the field creation](geo-shp.html#add-field)) named by the optional `field_name` input argument.
1. Runs [`gdal.Polygonize`](https://gdal.org/api/gdal_alg.html#_CPPv414GDALPolygonize15GDALRasterBandH15GDALRasterBandH9OGRLayerHiPPc16GDALProgressFuncPv) with:
    * `hSrcBand=raster_band`
    * `hMaskBand=None` (optional raster band to define polygons)
    * `hOutLayer=dst_layer`
    * `iPixValField=0` (if no field was be added, set to -1 in order to create `FID` field; if more field added, set to 1, 2, ... )
    * `papszOptions=[]` (no effect for `ESRI Shapefile` driver type)
    * `callback=None` for not using the reporting algorithm (`GDALProgressFunc()`)
1. Creates a `.prj` projection file (recall descriptions on the [shapefile page](geo-shp.html#prj-shp)) using the spatial reference system of the input `raster` with the [`get_srs`](geo-raster.html##lc-fun) function.   


```python
def raster2polygon(file_name, out_shp_fn, band_number=1, field_name="values"):
    """
    Convert a raster to polygon
    :param file_name: STR of target file name, including directory; must end on ".tif"
    :param out_shp_fn: STR of a shapefile name (with directory e.g., "C:/temp/poly.shp")
    :param band_number: INT of the raster band number to open (default: 1)
    :param field_name: STR of the field where raster pixel values will be stored (default: "values")
    :return: None
    """
    # ensure that the input raster contains integer values only and open the input raster
    file_name = float2int(file_name)
    raster, raster_band = open_raster(file_name, band_number=band_number)

    # create new shapefile with the create_shp function
    new_shp = create_shp(out_shp_fn, layer_name="raster_data", layer_type="polygon")
    dst_layer = new_shp.GetLayer()

    # create new field to define values
    new_field = ogr.FieldDefn(field_name, ogr.OFTInteger)
    dst_layer.CreateField(new_field)

    # Polygonize(band, hMaskBand[optional]=None, destination lyr, field ID, papszOptions=[], callback=None)
    gdal.Polygonize(raster_band, None, dst_layer, 0, [], callback=None)

    # create projection file
    srs = get_srs(raster)
    make_prj(out_shp_fn, int(srs.GetAuthorityCode(None)))
    print("Success: Wrote %s" % str(out_shp_fn))
```

{% include tip.html content="`Polygonize` can also be run as a [terminal command](geo-raster.html#terminal) with [`gdal_polygonize`](https://gdal.org/programs/gdal_polygonize.html)." %}

|     Both the `float2int` and the `raster2polygon` functions are also available in the `geo_utils` package ([`geo_tuils/geo_tools.py`](https://github.com/hydro-informatics/geo-utils/blob/master/geo_utils/geo_tools.py)).

Now we can use the `raster2polygon` function to convert the flow depth raster for 1000 cfs (`h001000.cfs` from the [*River Architect* sample datasets](https://github.com/RiverArchitect/SampleData/tree/master/01_Conditions/2100_sample)) to a polygon shapefile:


```python
src_raster = r"" +  os.path.abspath('') + "/geodata/river-architect/h001000.tif"
tar_shp = r"" + os.path.abspath('') + "/geodata/river-architect/h_poly_cls.shp"
raster2polygon(src_raster, tar_shp)
```

    Info: Creating integer raster: 
    >> C:\Users\schwindt\jupyter\hypy/geodata/river-architect/h001000_int.tif
    Success: Wrote C:\Users\schwindt\jupyter\hypy/geodata/river-architect/h_poly_cls.shp
    

{% include image.html file="qgis-h-polygonized.png" alt="polygonized" caption="The newly created polygon shapefile form the float-type h001000.tif raster plotted in QGIS. Note that the float numbers are classified in 8 integer bins ranging from 0 to 7 fps." %}

## Rasterize (vector shapefile to raster) {#shp2raster}

Similar to `gdal.Polygonize`, [`gdal.RasterizeLayer`](https://gdal.org/python/osgeo.gdal-module.html#RasterizeLayer) represents a powerful option to easily convert a shapefile into a raster. More precisely, a shapefile is not really converted but burned onto a raster. That means, values stored in a field of a shapefile feature are used (burned) as pixel values in a new raster. A little attention is required to ensure that the correct values and data types are used. So let's write a `rasterize` function that we can use robustly over and over again, avoiding potential headaches. The `rasterize` function:
1. Open the provided input shapefile name and its layer.
1. Reads the spatial extent of the layer.
1. Derives the solution as a function of the spatial extent and a user-defined `pixel_size` (optional argument).
1. Creates a new *GeoTIFF* raster using the
    * user-defined `output_raster_file_name`,
    * calculated x and y resolution, and
    * `eType` (default is `gdal.GDT_Float32` - recall all data type options listed on the [raster page](geo-raster.html#etypes).
1. Applies the geo-transformation defined by the source layer extents and the `pixel_size`.
1. Creates one raster `band`, fills the `band` with the user-defined `no_data_value` (default is `-9999`), and sets the `no_data_value`.
1. Sets the spatial reference system of the raster to the same as the source shapefile.
1. Applies `gdal.RasterizeLayer` with 
    * `dataset=target_ds` (target raster dataset),
    * `bands=[1]` (*list(integer)* - increase to defined more raster bands and assign other values, e.g., from other fields of the source shapefile),
    * `layer=source_lyr` (layer with features to burn to the raster),
    * `pfnTransformer=None` ([read more in the developer's docs](https://gdal.org/python/osgeo.gdal-module.html#RasterizeLayer)),
    * `pTransformArg=None` ([read more in the developer's docs](https://gdal.org/python/osgeo.gdal-module.html#RasterizeLayer)),
    * `burn_values=[0]` (a default value that is burned to the raster),
    * `options=["ALL_TOUCHED=TRUE"]` defines that all pixels touched by a polygon get the polygon's field value - if not set: only pixels that are entirely in the polygon get a value assigned,
    * `options=["ATTRIBUTE=" + str(kwargs.get("field_name"))]` defines the field name with values to burn.


```python
def rasterize(in_shp_file_name, out_raster_file_name, field_name, 
              pixel_size=10, no_data_value=-9999, dtype=gdal.GDT_Float32):
    """
    Converts any shapefile to a raster
    :param in_shp_file_name: STR of a shapefile name (with directory e.g., "C:/temp/poly.shp")
    :param out_raster_file_name: STR of target file name, including directory; must end on ".tif"
    :param pixel_size: INT of pixel size (default: 10)
    :param no_data_value: Numeric (INT/FLOAT) for no-data pixels (default: -9999)
    :param rdtype: gdal.GDALDataType raster data type - default=gdal.GDT_Float32 (32 bit floating point)
    :param field_name: name of the shapefile's field with values to burn to the raster
    :return: produces the shapefile defined with in_shp_file_name
    """

    # open data source
    source_ds = ogr.Open(in_shp_file_name)
    source_lyr = source_ds.GetLayer()

    # read extent
    x_min, x_max, y_min, y_max = source_lyr.GetExtent()

    # get x and y resolution
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)

    # create destination data source (GeoTIff raster)
    target_ds = gdal.GetDriverByName('GTiff').Create(out_raster_file_name, x_res, y_res, 1, eType=rdtype)
    target_ds.SetGeoTransform((x_min, pixel_size, 0, y_max, 0, -pixel_size))
    
    # get and fill band
    band = target_ds.GetRasterBand(1)
    band.Fill(no_data_value)
    band.SetNoDataValue(no_data_value)

    # get spatial reference system and assign to raster
    srs = get_srs(source_ds)
    srs.ImportFromEPSG(int(srs.GetAuthorityCode(None)))
    target_ds.SetProjection(srs.ExportToWkt())

    # RasterizeLayer(Dataset dataset, int bands, Layer layer, pfnTransformer=None, pTransformArg=None,
    # int burn_values=0, options=None, GDALProgressFunc callback=0, callback_data=None)
    gdal.RasterizeLayer(target_ds, [1], source_lyr, None, None, burn_values=[0],
                        options=["ALL_TOUCHED=TRUE", "ATTRIBUTE=" + str(kwargs.get("field_name"))])

    # release raster band
    band.FlushCache()
```

{% include tip.html content="`Rasterize` can also be run as a [terminal command](geo-raster.html#terminal) with [`gdal_rasterize`](https://gdal.org/programs/gdal_rasterize.html)." %}

Now we can use the `rasterize` function to convert the above polygonized flow depth polygon shapefile (`h_poly_cls.shp`) back to a raster (that is a little bit useless in practice, but an illustrative exercise). Pay attention to the data type, which is `gdal.GDT_Int32` and define the `field_name` correctly.


```python
src_shp = r"" + os.path.abspath('') + "/geodata/river-architect/h_poly_cls.shp"
tar_ras = r"" +  os.path.abspath('') + "/geodata/river-architect/h_re_rastered.tif"
rasterize(src_shp, tar_ras, pixel_size=5, rdtype=gdal.GDT_Int32, field_name="values")
```

{% include image.html file="qgis-h-rasterized.png" alt="rasterized" caption="The re-rasterized flow depth raster h_re_rastered.tif plotted in QGIS." %}