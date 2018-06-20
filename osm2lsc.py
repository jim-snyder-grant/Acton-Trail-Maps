#!/usr/bin/env python2
# Here is a python program to bring data down from OSM & transform it for use
# in LSC maps
# typical use: "python2 osm2lsc.py args..."

import requests  # for wget equivalent
import sys       # file operations
import os.path   # file name operations
from time import sleep  # rest
import re        # regular expressions as part of SED equivalent
from tempfile import mkstemp  # tempfile
import shutil    # higher level file operations
# For calling gdal functionality directly:
# from osgeo import ogr, osr, gdal, gdalconst
# For calling ogr2ogr instead of underlying gdal functionality:
import subprocess

regularArguments = {
    'bct', 'bike_trails', 'blue_trails', 'bounds', 'camping', 'green_trails',
    'outside_trails', 'parking', 'parking_street', 'red_trails', 'town',
    'town_land', 'unblazed_trails', 'yellow_trails'
}
allArg = 'all'
helpArg = "help"


def usage():
    print("Usage: python2 " + sys.argv[0] + " arguments ")
    print(" arguments are one or more of " + ','.join(sorted({allArg, helpArg} | regularArguments)))


if 1 == len(sys.argv):
    usage()
    exit(0)


if (sys.argv[1] == allArg):
    args = sorted(list(regularArguments))
else:
    args = sys.argv[1:]   # sys.argv[0] is the program name

# Box of area we are generating map for, also makes searches go more quickly
# than just using the Acton area test.
ACTON_BBOX = "[bbox:42.433,-71.5,42.534,-71.384];"
# Using an Acton Area ID lets us detect trails that are in the bounding box
# but not in Acton.
ACTON_AREA_ID = "3601832779"
# We get canoe launch by ID since it's a CR, not land owned by Acton
CANOE_LAUNCH_ID = "449483835"
# Generic trails filter includes paths and tracks.
TRAILS_FILTER = 'way[highway~"^path$|^track$"][access!~"^private$|^no$"][name'
# 'Special' trail names
SPECIAL_TRAIL = "Blue and Green Trail"
# Test to see if we are in Acton
IS_INSIDE_ACTON = "(area:"+ACTON_AREA_ID+")"
# Special post-processing if we got new bounds
got_new_bounds = False
got_new_town_land = False
# variable for time delay. We increase it if we get a too-many-requests error.
time_delay = 2
start_arg = args[0]


# helpful SED-lite worker function
def ourSED(inPattern, outPattern, filename):
    with open(filename, 'r') as fin:
        fid, tempName = mkstemp()
        inContents = fin.read()
        outContents = re.sub(inPattern, outPattern, inContents,
                             flags=re.MULTILINE | re.IGNORECASE)
        os.write(fid, outContents)
        os.close(fid)
    os.remove(filename)
    shutil.move(tempName, filename)


# Another worker function, to wrap the error handling of the 'call' function
def ourCall(args):
    try:
        output_text = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        print "Execution failed with code ", e.returncode
        print e.output
        exit(e.returncode)
    return output_text


# Diff returns 1 on success when there is a difference, so do not exit in that case
def ourDiffCall(args):
    try:
        output_text = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError, e:
        if 1 == e.returncode:
            return 1
        else:
            print "Execution failed with code ", e.returncode
            print e.output
            exit(e.returncode)
    return 0


for arg in args:
    # first time through, don't need to sleep
    if arg != start_arg:
        # we were getting too-many-requests errors.
        sleep(time_delay)

    # by default, extract lines. But exceptions are made below
    geometry = "lines"

    if arg == "bct":
        KMLcolor = "55FF78F0"
        filters = 'relation[name~"Bay Circuit Trail"];(._;>;)->.a;way.a(42.433,-71.5,42.534,-71.384)'
    elif arg == "bike_trails":
        KMLcolor = "501450FF"
        filters = 'way[highway="cycleway"]'+IS_INSIDE_ACTON
    elif arg == "blue_trails":
        KMLcolor = "ffff0000"
        filters = TRAILS_FILTER+'~"blue",i][name!~"'+SPECIAL_TRAIL+'"]'+IS_INSIDE_ACTON
    elif arg == "bounds":
        # Some bounds are multipolygons stored in OSM as 'relation', others are
        # plain old 'way'. And then there's the canoe launch, which isn't
        # owned by the town of Acton.
        KMLcolor = 'ffffffff'
        filters = '(way('+CANOE_LAUNCH_ID+');relation[boundary=protected_area][owner~"Town Of Acton",i];way[boundary=protected_area][owner~"Town Of Acton",i];)'
        geometry = "multipolygons"
        got_new_bounds = True
    elif arg == "camping":
        KMLcolor = "643C9614"
        filters = 'node[tourism=camp_site]'+IS_INSIDE_ACTON
        geometry = "points"
    elif arg == "green_trails":
        KMLcolor = "ff00AA14"
        filters = TRAILS_FILTER+'~"green",i][name!~"'+SPECIAL_TRAIL+'"]'+IS_INSIDE_ACTON
    elif arg == "outside_trails":
        KMLcolor = "ffff00ff"
        # This is all trails outside of Acton (but no private trails)
        filters = 'way[highway~"path|track|footway"][footway!~"sidewalk|crossing"][access!~"^private$|^no$|^customers$"]->.everything;(.everything; - way'+IS_INSIDE_ACTON+';)'
    elif arg == "parking":
        KMLcolor = "50BEBEBE"
        filters = 'way[amenity=parking][website~actontrails,i]'+IS_INSIDE_ACTON
        geometry = "multipolygons"
    elif arg == "parking_street":
        KMLcolor = "50BEBEBE"
        filters = 'node[amenity=parking][website~actontrails,i]'+IS_INSIDE_ACTON
        geometry = "points"
    elif arg == "red_trails":
        KMLcolor = "ff0000ff"
        filters = TRAILS_FILTER+'~"red",i]'+IS_INSIDE_ACTON
    elif arg == "town":
        KMLcolor = "ff00ff00"
        filters = 'area[wikipedia="en:Acton, Massachusetts"];rel(pivot)'
        geometry = "multipolygons"
    elif arg == "town_land":
        # Capture town land used as conservation, but not actually conservation, by looking for nature_reserve
        # which is not protected.
        KMLcolor = 'ffffffff'
        filters = '(way[leisure=nature_reserve][boundary!=protected_area][owner~"Town Of Acton",i];)'
        geometry = "multipolygons"
        got_new_town_land = True
    elif arg == "unblazed_trails":
        KMLcolor = "ffff00ff"
        # This is all the trails inside of Acton without special color names
        # (but no private trails), plus one special trail.
        filters = 'way[highway~"path|track"][access!~"^private$|^no$"][name!~"Red|Blue|Green|Yellow",i]->.unblazed; way[name="'+SPECIAL_TRAIL+'"]->.special; way'+IS_INSIDE_ACTON+'->.intown; (way.unblazed.intown; way.special.intown;)'
    elif arg == "yellow_trails":
        KMLcolor = " ff00ffff"
        filters = TRAILS_FILTER+'~"yellow",i]'+IS_INSIDE_ACTON
    elif arg == helpArg:
        usage()
        exit(0)
    else:
        print "ERROR: Invalid arg: " + arg
        exit(1)

    osmFile = arg + ".osm"

    # save the old OSM file for comparing with diff to see if there were really changes
    osmFileOld = arg + ".old.osm"
    if os.path.exists(osmFile):
        if os.path.exists(osmFileOld):
            os.remove(osmFileOld)
        os.rename(osmFile, osmFileOld)

    # osmDriver = gdal.GetDriverByName("OSM")
    # kmlDriver = gdal.GetDriverByName("KML")
    # geojsonDriver = gdal.GetDriverByName("GeoJSON")

    url = "http://overpass-api.de/api/interpreter?data="+ACTON_BBOX+filters+";(._;>;);out body;"
    response = requests.get(url)
    while 429 == response.status_code or 504 == response.status_code:
        time_delay = time_delay+3
        print "Too many requests: slowing down delay to ", time_delay, " seconds"
        if time_delay > 60:
            exit(1)
        sleep(time_delay)
        response = requests.get(url)

    if 200 != response.status_code:
        print "Status code: ", response.status_code, " on this request"
        print(url)
        exit(1)
    contents = response.text
    argFile = open(osmFile, 'w')
    argFile.write(contents)
    argFile.close()

    if os.path.exists(osmFile):
        print("created " + osmFile)
    else:
        print("ERROR: Did not create " + osmFile)
        exit(1)

    # Check to see if the OSM file has changed. We do this using diff and ignoring
    # the osm_base and osm version lines.
    if os.path.exists(osmFileOld):
        diff_return = ourDiffCall(['diff', "-Imeta osm_base", "-Iosm version", osmFile, osmFileOld])
        os.remove(osmFileOld)
    else:
        diff_return = 1

    if diff_return == 0:
        print ("No changes")
        # If there are no changes, then restore the old file with git checkout
        ourCall(['git', 'checkout', osmFile])

    else:

        # save the old KML for comparing in qgis
        kmlFile = arg + ".kml"
        if os.path.exists(kmlFile):
            kmlFileOld = arg + ".old.kml"
            if os.path.exists(kmlFileOld):
                os.remove(kmlFileOld)
            os.rename(kmlFile, kmlFileOld)

        ourCall(['ogr2ogr', '-f', 'KML', kmlFile, osmFile, geometry])

        # now put in special color for looking at KML in google earth
        ourSED("<color>........", "<color>"+KMLcolor, kmlFile)

        # convert to GeoJSON for importing into MapBox
        geojsonFile = arg + ".geojson"
        if os.path.exists(geojsonFile):
            os.remove(geojsonFile)

        ourCall(['ogr2ogr', '-f', 'GeoJSON', '-oo', 'CONFIG_FILE=./osmconf.actontrails.ini',geojsonFile, osmFile, geometry])

        # if it's the BCT, do post-processing to create a single segment from the individual ways
        if arg == "bct":
            ourCall(['ogr2ogr', "temp", geojsonFile])
            os.remove(geojsonFile)
            ourCall(['ogr2ogr', "-f", "GeoJSON", geojsonFile, "temp",
                     "-dialect", "sqlite", "-sql",
                     "SELECT ST_LineMerge(ST_Collect(geometry)) FROM OGRGeoJSON"])
            shutil.rmtree("temp")

        # just checking and announcing results
        if os.path.exists(kmlFile):
            print("created " + kmlFile)
        else:
            print("ERROR: Did not create " + kmlFile)
            exit(1)

        if os.path.exists(geojsonFile):
            print("created " + geojsonFile)
        else:
            print("ERROR: Did not create " + geojsonFile)
            exit(1)

    if got_new_bounds:
        ourSED(" Conservation Land", "", "bounds.geojson")
