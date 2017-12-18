#!/usr/bin/env python2
# Combine all the trail files into one, and create KML and geojson versions.

import os
from osgeo import ogr, gdal

# For combined files, retain geometry and name.
# For geojson add new field color=blue,red, yellow, green or black.
# For KML make sure Style/LineStyle/color gets
# corresponding 6-digit hex values.
# The hex colors are in OGR order "RRGGBBAA" not KML order "AABBGGRR"
# the driver does the conversion
file2style = {
    "yellow_trails":
        {"KML": "FFFF00FF", "COLOR": "yellow", "in_acton": True},
    "blue_trails":
        {"KML": "0000FFFF", "COLOR": "blue", "in_acton": True},
    "green_trails":
        {"KML": "14AA00FF", "COLOR": "green", "in_acton": True},
    "red_trails":
        {"KML": "FF0000FF", "COLOR": "red", "in_acton": True},
    "outside_trails":
        {"KML": "FF00FFFF", "COLOR": "black", "in_acton": False},
    "unblazed_trails":
        {"KML": "FF00FFFF", "COLOR": "black", "in_acton": True},
}

gdal.UseExceptions()

OUTFILEBASEALL = "all_trails"
OUTFILEBASEACTON = "acton_trails"

NAMEKEY = "name"


# geoJSON writing prep
COLORKEY = "color"
OSMKEY = "osm_id"
inExtension = r".geojson"
GeoJSONdriver = ogr.GetDriverByName("GeoJSON")

outfileAllJSON = GeoJSONdriver.CreateDataSource(OUTFILEBASEALL + '.geojson')
outfileActonJSON = GeoJSONdriver.CreateDataSource(OUTFILEBASEACTON + '.geojson')

outLayerAllJSON = outfileAllJSON.CreateLayer("OGRGeoJSON")
outLayerActonJSON = outfileActonJSON.CreateLayer("OGRGeoJSON")

colorfield = ogr.FieldDefn(COLORKEY, ogr. OFTString)
outLayerAllJSON.CreateField(colorfield)
outLayerActonJSON.CreateField(colorfield)

namefield = ogr.FieldDefn(NAMEKEY, ogr. OFTString)
outLayerAllJSON.CreateField(namefield)
outLayerActonJSON.CreateField(namefield)

osmfield = ogr.FieldDefn(OSMKEY, ogr. OFTString)
outLayerAllJSON.CreateField(osmfield)
outLayerActonJSON.CreateField(osmfield)

layerDefnJSON = outLayerAllJSON.GetLayerDefn()

# KML writing prep
KMLdriver = ogr.GetDriverByName("KML")
outfileAllKML = KMLdriver.CreateDataSource(OUTFILEBASEALL + '.kml')
outfileActonKML = KMLdriver.CreateDataSource(OUTFILEBASEACTON + '.kml')
outLayerAllKML = outfileAllKML.CreateLayer("lines")
outLayerActonKML = outfileActonKML.CreateLayer("lines")
outLayerAllKML.CreateField(colorfield)
outLayerActonKML.CreateField(colorfield)

layerDefnKML = outLayerAllKML.GetLayerDefn()


for base, info in file2style.items():
    inFile = base + inExtension
    # Second Open arg: 0 means read-only; 1 means writeable
    dataSource = GeoJSONdriver.Open(inFile, 0)
    inlayer = dataSource.GetLayer()
    layerDefinition = inlayer.GetLayerDefn()

    # This is an OGR style spec: http://www.gdal.org/ogr_feature_style.html
    # for writing into KML
    style = "PEN(c:#" + info["KML"] + ")"
    # this is the value we will put into the new 'color' property in the
    # geoJSON and KML files.
    color = info["COLOR"]
    # is this file holding data in Acton?
    in_acton = info["in_acton"]
    
    for infeature in inlayer:
    # read from source file
        geom = infeature.GetGeometryRef()
        name = infeature.GetField(NAMEKEY)
        osm_id = infeature.GetField(OSMKEY)
        
    # JSON writing part
        outfeatureJSON = ogr.Feature(layerDefnJSON)
        outfeatureJSON.SetGeometry(geom)
        outfeatureJSON.SetField(COLORKEY, color)
        if (name):
            outfeatureJSON.SetField(NAMEKEY, name)
        outfeatureJSON.SetField(OSMKEY, osm_id)
        outLayerAllJSON.CreateFeature(outfeatureJSON)
        if in_acton:
            outLayerActonJSON.CreateFeature(outfeatureJSON)
        outfeatureJSON = None
        
    # KML writing part
        outfeatureKML = ogr.Feature(layerDefnKML)
        outfeatureKML.SetGeometry(geom)
        outfeatureKML.SetStyleString(style)
        outfeatureKML.SetField(COLORKEY, color)
        if (name):
            outfeatureKML.SetField(NAMEKEY, name)
        outLayerAllKML.CreateFeature(outfeatureKML)
        if in_acton:
            outLayerActonKML.CreateFeature(outfeatureKML)
        outfeatureKML = None