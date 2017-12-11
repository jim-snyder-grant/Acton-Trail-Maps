#!/usr/bin/env python2
# combine all the trail files into one, 
# and create KML and geojson versions. 

# for combined files, retain geometry and name. 
# for geojson add new field color=blue,red, yellow, green or black.
# for KML make sure Style/LineStyle/color gets 
# corresponding 6-digit hex values. 
# the hex colors are in OGR order "RRGGBBAA" not KML order "AABBGGRR" 
# the driver does the conversion
file2style = {
    "yellow": 
        {"KML": "FFFF00FF", "JSON": "yellow"},
    "blue": 
        {"KML": "0000FFFF", "JSON": "blue"},
    "green": 
        {"KML": "14AA00FF", "JSON": "green"},
    "red": 
        {"KML": "FF0000FF", "JSON": "red"},
    "outside_trails": 
        {"KML": "FF00FFFF", "JSON": "black"},
    "unblazed_trails": 
        {"KML": "FF00FFFF", "JSON": "black"},    
}

import os
from osgeo import ogr,gdal
gdal.UseExceptions()

OUTFILEBASE = "alltrails"
NAMEKEY = "name"

# KML writing prep
KMLdriver = ogr.GetDriverByName("KML")
outfileKML = KMLdriver.CreateDataSource( OUTFILEBASE + '.kml' )
outLayerKML = outfileKML.CreateLayer("lines")
layerDefnKML = outLayerKML.GetLayerDefn()
    
#geoJSON writing prep
COLORKEY = "color"
OSMKEY = "osm_id"
inExtension = r".geojson"
GeoJSONdriver = ogr.GetDriverByName("GeoJSON")
outfileJSON = GeoJSONdriver.CreateDataSource( OUTFILEBASE + '.geojson' )
outLayerJSON = outfileJSON.CreateLayer("OGRGeoJSON")
outLayerJSON.CreateField(ogr.FieldDefn(COLORKEY, ogr. OFTString ))
outLayerJSON.CreateField(ogr.FieldDefn(NAMEKEY, ogr. OFTString ))
outLayerJSON.CreateField(ogr.FieldDefn(OSMKEY, ogr. OFTString ))
layerDefnJSON = outLayerJSON.GetLayerDefn()

for base,info in file2style.items():
    inFile = base + inExtension
    dataSource = GeoJSONdriver.Open(inFile, 0) # 0 means read-only. 1 means writeable.
    inlayer = dataSource.GetLayer()
    layerDefinition = inlayer.GetLayerDefn()

# This is an OGR style spec: http://www.gdal.org/ogr_feature_style.html for writing into KML   
    style = "PEN(c:#" + info["KML"] + ")"
# this is the value we will put into the new 'color' property in the geoJSON file.  
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
        outfeatureJSON.SetField(COLORKEY,color)
        if (name):
            outfeatureJSON.SetField(NAMEKEY, name)
        outfeatureJSON.SetField(OSMKEY, osm_id)    
        outLayerJSON.CreateFeature(outfeatureJSON)
        outfeatureJSON = None
        
outLayerKML = None  
outfileKML = None
outLayerJSON = None  
outfileJSON = None  

