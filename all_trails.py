#!/usr/bin/env python2
# Combine all the trail files into one, and create KML and geojson versions.

import os
import re
from osgeo import ogr, gdal

# For combined files, retain geometry, name, and 'highway' key (to detect railtrails)
# For geojson add new field color=blue, red, yellow, green or black.
# For KML make sure Style/LineStyle/color gets
# corresponding 6-digit hex values.
# The hex colors are in OGR order "RRGGBBAA" not KML order "AABBGGRR"
# the driver does the conversion
# This is a list at top level so the order remains the same.

RAILTRAILCOLOR = "FFA000FF" # orangey for railtrails, also sprinkled into outside_trails as needed 

file2style = [
    {"base": "blue_trails",     "KML": "0000FFFF", "COLOR": "blue", "in_acton": True},
    {"base": "outside_trails",  "KML": "FF00FFFF", "COLOR": "black", "in_acton": False},
    {"base": "yellow_trails",   "KML": "FFFF00FF", "COLOR": "yellow", "in_acton": True},
    {"base": "green_trails",    "KML": "14AA00FF", "COLOR": "green", "in_acton": True},
    {"base": "unblazed_trails", "KML": "FF00FFFF", "COLOR": "black", "in_acton": True},
    {"base": "red_trails",      "KML": "FF0000FF", "COLOR": "red", "in_acton": True},
    {"base": "bct",             "KML": "FF19FFFF", "COLOR": "fuschia", "in_acton": True},    
    {"base": "bike_trails",     "KML": RAILTRAILCOLOR, "COLOR": "brown", "in_acton": True},
    {"base": "bike_trails_extended",     "KML": RAILTRAILCOLOR, "COLOR": "brown", "in_acton": False},
]

gdal.UseExceptions()

OUTFILEBASEALL = "all_trails"
OUTFILEBASEACTON = "acton_trails"
BRIDGEKEY = "bridge"
COLORKEY = "color"
HIGHWAYKEY = "highway"  # yes this key is oddly named. It's an Open Street Map convention
NAMEKEY = "name"
SURFACEKEY = "surface"
WHEELCHAIRKEY = "wheelchair"

# geoJSON writing prep
OSMKEY = "osm_id"
inExtension = r".geojson"
GeoJSONdriver = ogr.GetDriverByName("GeoJSON")

outfileAllJSON = GeoJSONdriver.CreateDataSource(OUTFILEBASEALL + '.geojson')
outfileActonJSON = GeoJSONdriver.CreateDataSource(OUTFILEBASEACTON + '.geojson')

outLayerAllJSON = outfileAllJSON.CreateLayer("OGRGeoJSON")
outLayerActonJSON = outfileActonJSON.CreateLayer("OGRGeoJSON")

bridgefield = ogr.FieldDefn(BRIDGEKEY, ogr. OFTString)
outLayerAllJSON.CreateField(bridgefield)
outLayerActonJSON.CreateField(bridgefield)

colorfield = ogr.FieldDefn(COLORKEY, ogr. OFTString)
outLayerAllJSON.CreateField(colorfield)
outLayerActonJSON.CreateField(colorfield)

highwayfield = ogr.FieldDefn(HIGHWAYKEY, ogr. OFTString)
outLayerAllJSON.CreateField(highwayfield)
outLayerActonJSON.CreateField(highwayfield)

namefield = ogr.FieldDefn(NAMEKEY, ogr. OFTString)
outLayerAllJSON.CreateField(namefield)
outLayerActonJSON.CreateField(namefield)

osmfield = ogr.FieldDefn(OSMKEY, ogr. OFTString)
outLayerAllJSON.CreateField(osmfield)
outLayerActonJSON.CreateField(osmfield)

surfacefield = ogr.FieldDefn(SURFACEKEY, ogr. OFTString)
outLayerAllJSON.CreateField(surfacefield)
outLayerActonJSON.CreateField(surfacefield)

wheelchairfield = ogr.FieldDefn(WHEELCHAIRKEY, ogr. OFTString)
outLayerAllJSON.CreateField(wheelchairfield)
outLayerActonJSON.CreateField(wheelchairfield)

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
    style_railtrail = "PEN(c:#" + RAILTRAILCOLOR + ")"
    # is this file holding data in Acton?
    in_acton = info["in_acton"]
    # this is the value we will put into the new 'color' property in the
    # geoJSON and KML files.
    color = info["COLOR"]
    pattern = re.compile(color,flags=re.IGNORECASE)
    
    for infeature in inlayer:
    # read from source file
        geom = infeature.GetGeometryRef()
        try:
            bridge = infeature.GetField(BRIDGEKEY)
        except (ValueError, KeyError):
            bridge = ""
        try:
            highway = infeature.GetField(HIGHWAYKEY)
        except (ValueError, KeyError):
            highway = ""
        try:
            name = infeature.GetField(NAMEKEY)
        except (ValueError, KeyError):
            name = ""
        # remove the colors from the names of Acton trails
        if name:
            name = pattern.sub('',name)
        try:
            osm_id = infeature.GetField(OSMKEY)
        except (ValueError, KeyError):
            osm_id = "Fake_osm_id"
        try:
            surface = infeature.GetField(SURFACEKEY)
        except (ValueError, KeyError):
            surface = ""
        try:
            wheelchair = infeature.GetField(WHEELCHAIRKEY)
        except (ValueError, KeyError):
            wheelchair = ""
        
    # JSON writing part
        outfeatureJSON = ogr.Feature(layerDefnJSON)
        outfeatureJSON.SetGeometry(geom)
        if (bridge):
            outfeatureJSON.SetField(BRIDGEKEY, bridge)
        outfeatureJSON.SetField(OSMKEY, osm_id)
        outfeatureJSON.SetField(COLORKEY, color)
        outfeatureJSON.SetField(HIGHWAYKEY, highway)
        if (name):
            outfeatureJSON.SetField(NAMEKEY, name)
        outfeatureJSON.SetField(OSMKEY, osm_id)
        if (surface):
            outfeatureJSON.SetField(SURFACEKEY, surface)
        outLayerAllJSON.CreateFeature(outfeatureJSON)
        if (wheelchair):
            outfeatureJSON.SetField(WHEELCHAIRKEY, wheelchair)
        outfeatureJSON.SetField(OSMKEY, osm_id)
        if in_acton:
            outLayerActonJSON.CreateFeature(outfeatureJSON)
        outfeatureJSON = None
        
    # KML writing part
        outfeatureKML = ogr.Feature(layerDefnKML)
        outfeatureKML.SetGeometry(geom)
        if (highway == "cycleway"):
            outfeatureKML.SetStyleString(style_railtrail)
        else:
            outfeatureKML.SetStyleString(style)
        outfeatureKML.SetField(COLORKEY, color)
        if (name):
            outfeatureKML.SetField(NAMEKEY, name)
        outLayerAllKML.CreateFeature(outfeatureKML)
        if in_acton:
            outLayerActonKML.CreateFeature(outfeatureKML)
        outfeatureKML = None
