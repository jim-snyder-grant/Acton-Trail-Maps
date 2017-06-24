#!/usr/bin/env python
# Here is a python program to bring data down from OSM & transform it for use in LSC maps
# typical use: "python osm2lsc.py args..."

import requests # for wget equivalent
import sys #file operations
import os.path # file name operations
from time import sleep #rest
import re# regular expressions as part of SED equivalent
from tempfile import mkstemp # tempfile
import shutil # higher level file operations
# For calling gdal functionality directly:
# from osgeo import ogr, osr, gdal, gdalconst
# For calling ogr2ogr instead of underlying gdal functionality:
from subprocess import call
 
EXIT_STATUS=0

regularArguments = {'red', 'blue', 'yellow', 'green','othertrails','bounds','town','parking','camping','bct','bfrt'}
allArg = 'all'
helpArg = "help"

def usage():
    print("Usage: python " + sys.argv[0] + " arguments ")
    print (" arguments are one or more of " + ','.join( sorted ({allArg, helpArg} | regularArguments)))
   

if (1 == len(sys.argv)):
    usage()
    EXIT_STATUS=1
    exit(EXIT_STATUS);


if (sys.argv[1] == allArg):
    args = list(regularArguments)
else:
    args = sys.argv[1:]   # sys.argv[0] is the program name

# Using a bounding box makes the searches go more quickly
ACTON_BBOX="[bbox:42.433,-71.5,42.534,-71.384];"
 # using an Acton Area ID lets us skip trails that are in the bounding box but not in Acton. 
ACTON_AREA_ID="3601832779"
 # we get canoe launch by ID since it's a conservation restriction not owned by Acton
CANOE_LAUNCH_ID="449483835"
 # generic trails filter includes paths and tracks. We removed 'footway' after editing to
 # remove that use for trails in Acton 
TRAILS_FILTER="way[\"highway\"~\"path|track\"][access!=private][\"name\""
# for trails, we surpress special treatment for trails that are entirely outside Acton 
AREA_FILTER="(area:"+ACTON_AREA_ID+")"
 # special post-processing if we got new bounds
GOT_NEW_BOUNDS=False

for arg in args:
    # by default, extract lines. But exceptions are made below 
    geometry="lines"   

    if arg == "bounds":
   # some bounds are multipolygons stored in OSM as 'relation', others are plain old 'way'.
   # and then there's the canoe launch, which isn't owned by the town of Acton
   # we are in a transition away from landuse=conservation
       filters="(way("+CANOE_LAUNCH_ID+ ");relation[\"boundary\"=\"protected_area\"][\"owner\"~\"Town Of Acton\",i];way[\"boundary\"=\"protected_area\"][\"owner\"~\"Town Of Acton\",i];relation[\"leisure\"=\"nature_reserve\"][\"owner\"~\"Town Of Acton\",i];way[\"leisure\"=\"nature_reserve\"][\"owner\"~\"Town Of Acton\",i])"
       KMLcolor="ffffffff"
       AREA_FILTER=""
       geometry="multipolygons"
       GOT_NEW_BOUNDS=True
    elif arg == "red":
        KMLcolor="ff0000ff"
        filters=TRAILS_FILTER+'~"'+arg+'",i]'
    elif arg == "blue":
        KMLcolor="ffff0000"
        filters=TRAILS_FILTER+'~"'+arg+'",i]'
    elif arg == "yellow":
        KMLcolor="ff00ffff"
        filters=TRAILS_FILTER+'~"'+arg+'",i]'
    elif arg == "green":
        KMLcolor="ff00AA14"
        filters=TRAILS_FILTER+'~"'+arg+'",i]'
    elif arg == "othertrails":
        KMLcolor="ffff00ff"
        filters=TRAILS_FILTER+'!~\"Red|Blue|Green|Yellow\",i]'
    elif arg == "town":
        KMLcolor="ff00ff00"
        filters="area[wikipedia=\"en:Acton, Massachusetts\"];rel(pivot)"
        geometry="multipolygons"
        AREA_FILTER=""
    elif arg == "parking":
        KMLcolor="50BEBEBE"
        filters="way[\"amenity\"=\"parking\"][\"website\"~\"actontrails\",i]"
        geometry="multipolygons"
    elif arg == "camping":
        KMLcolor="643C9614"
        filters="node[\"tourism\"=\"camp_site\"]"
        geometry="points" 
    elif arg == "bct":
        KMLcolor="55FF78F0"  
        filters="relation[\"name\"~\"Bay Circuit Trail\"];(._;>;)->.a;way.a(42.433,-71.5,42.534,-71.384)"
        AREA_FILTER=""
    elif arg == "bfrt":
        KMLcolor="501450FF"  
        filters="way[\"name\"=\"Bruce Freeman Rail Trail: Phase 2 (proposed)\"]"
        AREA_FILTER=""
    elif arg == helpArg:
        usage()
        exit (EXIT_STATUS)
    else:
        print ("ERROR: Invalid arg: " + arg)
        EXIT_STATUS=1
        exit (EXIT_STATUS) 
 
	
    osmFile = arg + ".osm"
    kmlFile = arg + ".kml"
    backupFile = arg + ".old.kml"
    geojsonFile = arg + ".geojson"
#    osmDriver = gdal.GetDriverByName("OSM")
#    kmlDriver = gdal.GetDriverByName("KML")
#    geojsonDriver = gdal.GetDriverByName("GeoJSON")
 
    url = "http://overpass-api.de/api/interpreter?data="+ACTON_BBOX+filters+AREA_FILTER+";(._;>;);out body;"
    response = requests.get(url)
    contents = response.text
    argFile = open(osmFile, 'w')
    argFile.write(contents)
    argFile.close()
    
    if os.path.exists(osmFile):
	    print ("created "  + osmFile)
    else:
        print ("ERROR: Did not create " + osmFile)
        EXIT_STATUS=1
        exit (EXIT_STATUS) 
    
    #save the old KML for comparing in qgis
    if os.path.exists(kmlFile):
        if os.path.exists(backupFile):
             os.remove(backupFile)
        os.rename(kmlFile, backupFile)
    
    call(['ogr2ogr', '-f', 'KML', kmlFile, osmFile, geometry])
    
    def ourSED(inPattern, outPattern, filename):
        with open(filename, 'r') as fin:
            fid, tempName = mkstemp()
            inContents = fin.read()
            outContents = re.sub(inPattern, outPattern, inContents, flags=re.MULTILINE | re.IGNORECASE)
            os.write(fid,outContents)
            os.close(fid)
        os.remove(filename)
        os.rename(tempName, filename)  
    
    # now put in special color for looking at KML in google earth
    ourSED("<color>........", "<color>"+KMLcolor, kmlFile)   
    
    # convert to GeoJSON for importing into MapBox
    if os.path.exists(geojsonFile):
        os.remove(geojsonFile)

    call(['ogr2ogr', '-f', 'GeoJSON', geojsonFile, osmFile, geometry])    
    
     # if it's the BCT, do post-processing to create a single segment from the individual ways
    if arg == "bct":
        call(['ogr2ogr', "temp", geojsonFile])    
        os.remove(geojsonFile)
        call(['ogr2ogr', "-f", "GeoJSON", geojsonFile, "temp", "-dialect", "sqlite", "-sql", "SELECT ST_LineMerge(ST_Collect(geometry)) FROM OGRGeoJSON"])    
        shutil.rmtree("temp") 

    # ogr2ogr emits geoJSON v 1.0. MapBox needs the successor, RFC 7946. 
    # The key difference is that we must remove the crs line
    ourSED(r"^.crs.*$", "", geojsonFile)    
    
    # just checking and announcing results
    if os.path.exists(kmlFile):
	    print ("created "  + kmlFile)
    else:
	    print ("ERROR: Did not create " + kmlFile)
	    EXIT_STATUS=1
    
    if os.path.exists(geojsonFile):
	    print ("created "  + geojsonFile)
    else:
	    print ("ERROR: Did not create " + geojsonFile)
	    EXIT_STATUS=1
# we were getting too-many-requests errors.
    sleep(6)
    
if GOT_NEW_BOUNDS:
     ourSED (" Conservation Land","", "bounds.geojson")
    
exit (EXIT_STATUS)    


