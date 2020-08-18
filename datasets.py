#!/usr/bin/env python2

# first argument is an operation code, currently either 'compare' or 'update"

# The second argument will be assumed to be a filename, filetype geojson.
# which correspond to a mapbox dataset of the same name.

# Only works if the environment has an approprately set MAPBOX_ACCESS_TOKEN

import sys       # for command-line arguments
import json
from mapbox import Datasets
from mapbox import errors
import pprint

pp = pprint.PrettyPrinter()

arg1 = ["compare", "update"]


def usage():
    print("Usage: python2 " + sys.argv[0] + " '" + arg1[0] + "'|'" + arg1[1] + "' dataset-name")
    print("'compare' will report on differences between a local file with a geojson extension, and a mapbox dataset of the same name. ")
    print("'update' will make the same report, and also make the dataset match the file")

if 3 != len(sys.argv):
    usage()
    exit(0)

operation = sys.argv[1]

if operation not in arg1:
    usage()
    exit(0)

doUpdates = operation == arg1[1]

dsName = sys.argv[2]
print("processing ", dsName)
print ("Will do updates" if doUpdates else "Will not do updates")

fName = dsName + '.geojson'


def float6(s):
    # mapbox truncates to 6 sig digits,
    # so let's do the same for comparisons
    parts = s.partition('.')
    return float(parts[0] + parts[1] + parts[2][0:6])

try:
    with open(fName) as data_file:
        newFromFile = json.load(data_file, parse_float=float6)
# parent of IOError, OSError *and* WindowsError where available
except EnvironmentError:
    print('oops - are you sure there is a <', fName, '> file there?')
    exit()

# pp.pprint (newFromFile)
newDict = {}
for feat in newFromFile['features']:
    # regularize the use of osm_id (OSM sometimes uses osm_way_id instead
    osm_id = None
    osm_way_id = None
    
    if 'osm_id' in feat['properties']:
        osm_id = feat['properties']['osm_id']
    if 'osm_way_id' in feat['properties']:
        osm_way_id = feat['properties']['osm_way_id']
    
    if (osm_id is None):
        osm_id = osm_way_id
#    pp.pprint (feat)
#    print ('id / way id', osm_id, osm_way_id)
    feat['properties']['osm_id'] = osm_id
    newDict [osm_id] = feat
    #try:
    #    name = feat['properties']['name'];
    # except KeyError:
    #    name = "(no name)"
    # print ("name=", name," id=",id)
print('new file has ',len(newDict),' features')

datasets = Datasets()

try:
    listings = datasets.list().json()
except errors.TokenError as exc:
    print("Hey, get yourself a valid MapBox token")
    exit()
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

oldDataset = None
for ds in listings:
    if ds.get('name', "") == dsName:
        oldDataset = ds
        break
if oldDataset:
    print("found match for dataset", dsName)
else:
    print("no match for dataset", dsName)
    exit()

dsId = oldDataset['id']
print("dataset %s has %d features" % (dsName, oldDataset['features']))

noChanges = True

oldFeatures = datasets.list_features(dsId).json()['features']

for oldFeat in oldFeatures:
    newFeat = newDict.pop(oldFeat['properties']['osm_id'], None)
    if not newFeat:
        print("!-----Existing feature not found in input:")
        noChanges = False
        pp.pprint(oldFeat)
        if doUpdates:
            retval = datasets.delete_feature(dsId, oldFeat['id'])
            if retval.status_code in (200,204):
                print("deletion succeeded")
            else:
                print("HTTP response code to deleting feature: ", retval.status_code)
    else:
        changedGeom = newFeat['geometry'] != oldFeat['geometry']
        changedProps = newFeat['properties'] != oldFeat['properties']
        if changedGeom:
            print ("!-----Changed Geometry")
        if changedProps:
            print ("!-----Changed Properties")
        if changedProps or changedGeom:
            noChanges = False
            print("OLD FEATURE:")
            pp.pprint(oldFeat)
            print("NEW FEATURE:")
            pp.pprint(newFeat)
            if doUpdates:
                retval = datasets.update_feature(dsId, oldFeat['id'], newFeat)
                if retval.status_code in (200,204):
                    print("update succeeded")
                else:
                    print("HTTP response code to updating feature: ", retval.status_code)
# Any features not mapped earlier will remain in dictionary, and can be
# added now.  
        
if len(newDict):

    for id, newFeat in newDict.items():
        print("!-----New feature:")
        noChanges = False
        try:
            name = newFeat['properties']['name'];
        except KeyError:
            name = "(no name)"
        print ("name=", name," id=",id)
        if doUpdates:
            retval = datasets.update_feature(dsId, id, newFeat)
            if retval.status_code in (200,204):
                print("update succeeded")
            else:
                print("HTTP response code to adding new feature: ", retval.status_code)
if noChanges:
    print("No differences found")
