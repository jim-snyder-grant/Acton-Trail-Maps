import os
from osgeo import ogr,gdal
import yaml

gdal.UseExceptions()

with open("lands.yaml", 'r') as stream:
    try:
        landInfo = yaml.load(stream) 
    except yaml.YAMLError as exc:
        print(exc)

NAMEKEY = "name"
TRAILKEY = "trails"
LABELSIZEKEY = "labelsize"  # so far, just '1' for lands that have no trails, and '2' for lands that do. 
inFile = r"bounds.geojson"

GeoJSONdriver = ogr.GetDriverByName("GeoJSON")
dataSource = GeoJSONdriver.Open(inFile, 0) # 0 means read-only. 1 means writeable.
inlayer = dataSource.GetLayer()
layerDefinition = inlayer.GetLayerDefn()

outfile = GeoJSONdriver.CreateDataSource( 'bounds_centroids.geojson' )
outLayer = outfile.CreateLayer("centroids")
# Add fields
nameField = ogr.FieldDefn(NAMEKEY, ogr. OFTString )
outLayer.CreateField(nameField)
labelSizeField = ogr.FieldDefn(LABELSIZEKEY, ogr. OFTInteger )
outLayer.CreateField(labelSizeField)

for infeature in inlayer:
    geom = infeature.GetGeometryRef()
    name = infeature.GetField(NAMEKEY)
    if (name):
        if name in landInfo:
            # print name, landInfo [name]
            hasTrails = landInfo [name][TRAILKEY]
            labelsize = 2 if hasTrails else 1 
            # Create the feature and set values
            featureDefn = outLayer.GetLayerDefn()
            outfeature = ogr.Feature(featureDefn)
            outfeature.SetGeometry(geom.Centroid())
            outfeature.SetField(NAMEKEY, name)
            outfeature.SetField(LABELSIZEKEY, labelsize)
            outLayer.CreateFeature(outfeature)
            outfeature = None
        else:
            print "oops, no landInfo for ", name,"fix lands.yaml"
    # else: it's OK for there to be lands without names. Just keep moving...
outLayer = None  
outfile = None    
