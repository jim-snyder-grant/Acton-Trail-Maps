#!/usr/bin/env python2
import os
from osgeo import ogr, gdal
import yaml

gdal.UseExceptions()

with open("lands.yaml", 'r') as stream:
    try:
        landInfo = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
# this is for capturing the envelope data        
envjs = open("webpage/envelopes.js", "w");
envjs.write("var Envelopes = {\n")

LandsWithTrails=[];
        
NAMEKEY = "name"
URLKEY = "website"
TRAILKEY = "trails"
# So far, just '1' for lands that have no trails, and '2' for lands that do.
LABELSIZEKEY = "labelsize"
OSMKEY = "osm_id"
OSMWAYKEY = "osm_way_id" # sometimes OSM uses a way id and not an osm_id
inFile = r"bounds.geojson"

GeoJSONdriver = ogr.GetDriverByName("GeoJSON")
# Open second arg: 0 means read-only; 1 means writeable.
dataSource = GeoJSONdriver.Open(inFile, 0)
inlayer = dataSource.GetLayer()
layerDefinition = inlayer.GetLayerDefn()

outfile = GeoJSONdriver.CreateDataSource('bounds_centroids.geojson')
outLayer = outfile.CreateLayer("centroids")
# Add fields
nameField = ogr.FieldDefn(NAMEKEY, ogr. OFTString)
outLayer.CreateField(nameField)
labelSizeField = ogr.FieldDefn(LABELSIZEKEY, ogr. OFTInteger)
outLayer.CreateField(labelSizeField)
osmField = ogr.FieldDefn(OSMKEY, ogr. OFTString)
outLayer.CreateField(osmField)

for infeature in inlayer:
    geom = infeature.GetGeometryRef()
    name = infeature.GetField(NAMEKEY)
    osm_id = infeature.GetField(OSMKEY)
    osm_way_id = infeature.GetField(OSMWAYKEY)
    if (osm_id is None):
        osm_id = osm_way_id
    
    if (name):
        if name in landInfo:
            # print name, landInfo [name]
            hasTrails = landInfo[name][TRAILKEY]
            labelsize = 2 if hasTrails else 1
            if hasTrails:
                LandsWithTrails.append(name);     
            # Create the feature and set values
            featureDefn = outLayer.GetLayerDefn()
            outfeature = ogr.Feature(featureDefn)
            outfeature.SetGeometry(geom.Centroid())
        
            # Get Envelope returns a tuple (minX, maxX, minY, maxY)
            env = geom.GetEnvelope()
            url = infeature.GetField(URLKEY)
            envjs.write( "\"%s\": {\"envelope\":[[%f,%f], [%f,%f]],\"url\":\"%s\"},\n" %(name, env[0],env[2],env[1],env[3],url))
            
            outfeature.SetField(NAMEKEY, name)
            outfeature.SetField(LABELSIZEKEY, labelsize)
            outfeature.SetField(OSMKEY, osm_id)
            outLayer.CreateFeature(outfeature)
            outfeature = None
        else:
            print "oops, no landInfo for ", name, "fix lands.yaml"
    # else: it's OK for there to be lands without names. Just keep moving...
outLayer = None
outfile = None
envjs.write("};\n")
# now create the dropdown of lands with trails
dropdown = open("webpage/dropdown.html", "w");
for name in sorted(LandsWithTrails):
    dropdown.write(r'<li><a href="#!">'+name+r'</a></li>'+'\n');



