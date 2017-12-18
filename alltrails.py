#!/usr/bin/env python2
# Combine all the trail files into one, and create KML and geojson versions.

import os
from osgeo import ogr, gdal

# For combined files, retain geometry and name.
# For geojson add new field color=blue, red, yellow, green or black.
# For KML make sure Style/LineStyle/color gets
# corresponding 6-digit hex values.
# The hex colors are in OGR order "RRGGBBAA" not KML order "AABBGGRR"
# the driver does the conversion
# This is a list at top level so the order remains the same.
file2style = [
    {"base": "blue_trails",     "KML": "0000FFFF", "JSON": "blue"},
    {"base": "outside_trails",  "KML": "FF00FFFF", "JSON": "black"},
    {"base": "yellow_trails",   "KML": "FFFF00FF", "JSON": "yellow"},
    {"base": "green_trails",    "KML": "14AA00FF", "JSON": "green"},
    {"base": "unblazed_trails", "KML": "FF00FFFF", "JSON": "black"},
    {"base": "red_trails",      "KML": "FF0000FF", "JSON": "red"},
]

gdal.UseExceptions()

OUTFILEBASE = "all_trails"
NAMEKEY = "name"

# KML writing prep
KMLdriver = ogr.GetDriverByName("KML")
outfileKML = KMLdriver.CreateDataSource(OUTFILEBASE + '.kml')
outLayerKML = outfileKML.CreateLayer("lines")
layerDefnKML = outLayerKML.GetLayerDefn()

# geoJSON writing prep
COLORKEY = "color"
OSMKEY = "osm_id"
inExtension = r".geojson"
GeoJSONdriver = ogr.GetDriverByName("GeoJSON")
outfileJSON = GeoJSONdriver.CreateDataSource(OUTFILEBASE + '.geojson')
outLayerJSON = outfileJSON.CreateLayer("OGRGeoJSON")
outLayerJSON.CreateField(ogr.FieldDefn(COLORKEY, ogr. OFTString))
outLayerJSON.CreateField(ogr.FieldDefn(NAMEKEY, ogr. OFTString))
outLayerJSON.CreateField(ogr.FieldDefn(OSMKEY, ogr. OFTString))
layerDefnJSON = outLayerJSON.GetLayerDefn()

for info in file2style:
    base = info["base"]
    inFile = base + inExtension
    # Second Open arg: 0 means read-only; 1 means writeable
    dataSource = GeoJSONdriver.Open(inFile, 0)
    inlayer = dataSource.GetLayer()
    layerDefinition = inlayer.GetLayerDefn()

    # This is an OGR style spec: http://www.gdal.org/ogr_feature_style.html
    # for writing into KML
    style = "PEN(c:#" + info["KML"] + ")"
    # this is the value we will put into the new 'color' property in the
    # geoJSON file.
    color = info["JSON"]

    for infeature in inlayer:
        # read from source file
        geom = infeature.GetGeometryRef()
        name = infeature.GetField(NAMEKEY)
        osm_id = infeature.GetField(OSMKEY)
        # KML writing part
        outfeatureKML = ogr.Feature(layerDefnKML)
        outfeatureKML.SetGeometry(geom)
        outfeatureKML.SetStyleString(style)
        if (name):
            outfeatureKML.SetField(NAMEKEY, name)
        outLayerKML.CreateFeature(outfeatureKML)
        outfeatureKML = None

        # JSON writing part
        outfeatureJSON = ogr.Feature(layerDefnJSON)
        outfeatureJSON.SetGeometry(geom)
        outfeatureJSON.SetField(COLORKEY, color)
        if (name):
            outfeatureJSON.SetField(NAMEKEY, name)
        outfeatureJSON.SetField(OSMKEY, osm_id)
        outLayerJSON.CreateFeature(outfeatureJSON)
        outfeatureJSON = None

outLayerKML = None
outfileKML = None
outLayerJSON = None
outfileJSON = None 
