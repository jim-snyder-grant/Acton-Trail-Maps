# Acton-Trail-Maps
sources &amp; bug tracking &amp; scripts for the next generation of trail maps for Acton, MA, USA
getosm - shell file to extract data from OSM
creates the following files
red' 'blue' 'yellow' 'green' 'othertrails' 'bounds' 'town' 'parking' 'camping' 'BCT'
with .osm, .kml and .json extensions. 

A manual process is needed to then create bounds_centroids.geojson:
1) Open QGIS and open a new project with CRS EPSG:4326
2) Open the vector layer file bounds.geojson 
3) Choose Vector >> Geometry Tools >> Polygon Centroids
4) Options in dialog:
   "input layer" is the bounds layer you just opened
   "Centroids" has "Create Temporary Layer"
   "Open Output File" is checked 
   click on RUN
5) Choose Layer >>Save As
6) Options in dialog:
  Format:  GeoJSON
  Filename: bounds_centroids
  CRS is still EPSG:4326
  the other options are irrelevant it seems
7) After exiting QGIS (no need to save the project) and returning to the command line, the following command is needed:
sed -i s/\"crs.*$// bounds_centroids.geojson
