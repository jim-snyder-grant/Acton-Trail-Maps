#!/usr/bin/env python2
# Combine the two parking files (points and polygons) into one new one.

import os
import re
from osgeo import ogr, gdal

basenames = [
    {"base": "parking"    },
    {"base": "parking_street"},
]

gdal.UseExceptions()

OUTFILEBASE = "all_parking"

# geoJSON writing prep
OSMKEY = "osm_id"
OSMWAYKEY = "osm_way_id"
inExtension = r".geojson"
GeoJSONdriver = ogr.GetDriverByName("GeoJSON")

outfileJSON = GeoJSONdriver.CreateDataSource(OUTFILEBASE + '.geojson')
outLayerJSON = outfileJSON.CreateLayer("OGRGeoJSON")

osmfield = ogr.FieldDefn(OSMKEY, ogr. OFTString)
outLayerJSON.CreateField(osmfield)

layerDefnJSON = outLayerJSON.GetLayerDefn()

for info in basenames:
    base = info["base"]
    inFile = base + inExtension
    # Second Open arg: 0 means read-only; 1 means writeable
    dataSource = GeoJSONdriver.Open(inFile, 0)
    inlayer = dataSource.GetLayer()
    layerDefinition = inlayer.GetLayerDefn()

    for infeature in inlayer:
    # read from source file
        geom = infeature.GetGeometryRef()
        try:
            osm_id = infeature.GetField(OSMWAYKEY)
        except ValueError:
            osm_id = infeature.GetField(OSMKEY)       
                
        outfeatureJSON = ogr.Feature(layerDefnJSON)
        outfeatureJSON.SetGeometry(geom)
        outfeatureJSON.SetField(OSMKEY, osm_id)
               
        outLayerJSON.CreateFeature(outfeatureJSON)
        outfeatureJSON = None