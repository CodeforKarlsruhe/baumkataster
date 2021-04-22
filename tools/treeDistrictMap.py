#!/usr/bin/python3
# -*- coding: utf-8 -*-
""" Create data files for codefor karlsruhe baumkataster map

    Input (urls see below)
        baum-ka.json
            List of trees (baumkataster file from transparenzportal)
        bevolkerung-wohnberechtigte-bevolkerung.csv
            List of Population data from transparenzportal
        landtagswahl_2016_wahlbezirke.geojson
            Electron district list with geojson polygons, from transparenzportal
        treeUrls.json
            User supplied additional tree type information, e.g. url to wikidata

    Output. NB: leaflet coordinates are revered to standard geojson coordinates
        trees.json
            Annotated tree file for map.
        districtsLeaf.json
            City district polygons
        treeTypes.json
            Number of trees by type
        merged_landtagswahl_2016_wahlbezirke.geojson
            City distric polygons in standard format, just for information

    Copy trees.json, districtsLeaf.json and treeTypes.json to
    baumkataster/assets
        
"""

import sys
from pathlib import Path
from shapely.geometry import Point, Polygon
from area import area
import csv
import json
import geojson
# new 20210416. most stuff is still without pandas
import pandas as pd

# KA Center
CENTER = {"lat":49.00923, "lon":8.40391}

# currently we use stored files, but we can also try to load the data sources directly like so
# data sources:
# karlsruhe election districts :
# www: https://transparenz.karlsruhe.de/dataset/landtagswahl-2016/resource/a16d5625-4407-427b-9bc2-b5ce738d283c
# api: https://transparenz.karlsruhe.de/api/3/action/resource_show?id=a16d5625-4407-427b-9bc2-b5ce738d283c
# json: https://transparenz.karlsruhe.de/dataset/c6576352-5ece-4380-a837-1e454606bacd/resource/a16d5625-4407-427b-9bc2-b5ce738d283c/download/landtagswahl_2016_wahlbezirke.geojson

# karlsruhe baumkataster:
# www: https://transparenz.karlsruhe.de/dataset/fachplane-baumkataster
# api: https://transparenz.karlsruhe.de/api/3/action/package_show?id=fcdceb2e-d16d-410c-ba0f-521ba8c6effa
# json: https://geoportal.karlsruhe.de/server/rest/services/Fachplaene/Baumkataster/MapServer/1/query?where=ARTDEUT+IS+NOT+NULL&outFields=ARTDEUT%2CARTLAT&returnGeometry=true&f=geojson

# karlsuhe population:
# www: https://transparenz.karlsruhe.de/dataset/bevolkerung/resource/71ef348f-0f5b-46a0-8250-e87aae9f91bd
# api: https://transparenz.karlsruhe.de/api/3/action/resource_show?id=71ef348f-0f5b-46a0-8250-e87aae9f91bd
# csv: https://transparenz.karlsruhe.de/dataset/74561f6a-4783-4d70-b86a-008deec09441/resource/71ef348f-0f5b-46a0-8250-e87aae9f91bd/download/bevolkerung-wohnberechtigte-bevolkerung.csv


# two load the json or geojson directly from the url use the following:
#import urllib.request
#u = "https://...." # see above
#try:
#    url =  urllib.request.urlopen(u)
#except:
#    #something
#data = json.loads(url.read().decode("utf8"))

# for csv files use the following: (NB:url opening is identical)
#u = "https://...." # see above
#try:
#   url =  urllib.request.urlopen(u)  # no encoding here
#except:
#   something
#raw = url.read().decode("utf8")  # read with encding here
#data = csv.DictReader(raw, delimiter=", ", quotechar="\"", quoting=csv.QUOTE_MINIMAL)  # dict reader on the decoded content

# initialize globals
globs = {"pop":0, "area":0, "districts":0, "trees":0}

######################################################
def loadDistricts(file):
    # check districts geojson file
    df = Path(file)
    if df.is_file():
        print("District file exists")
        with open(df, "r", encoding='utf-8') as f:
            d = json.load(f)
            f.close()
        return d["features"]
    else:
        return None


######################################################
def loadElectRegions(file):
    gf = Path(file)
    if gf.is_file():
        print("Elect Regions file exists")
        with open(gf, "r", encoding='utf-8') as f:
            w = json.load(f)
            f.close()
        # get features
        wb = w["features"]
        print("Anzahl Bezirke: ", len(wb))

    else:
        print("No file:", gf)
        return None

    # read and merge polygons
    # note are are also MultiPolygons !
    po = dict()
    ds = dict()
    for w in wb:
        d = int(w["properties"]["Stadtteilnummer"])
        if w["geometry"]["type"] == "Polygon":
            c = w["geometry"]["coordinates"][0]
            p = Polygon(c)
            if po.get(d) == None:
                po[d] = [p]
                ds[d] = w["properties"]["Stadtteilname"]
            else:
                po[d].append(p)
        elif w["geometry"]["type"] == "MultiPolygon":
            m = w["geometry"]["coordinates"][0]
            for c in m:
                p = Polygon(c)
                if po.get(d) == None:
                    po[d] = [p]
                    ds[d] = w["properties"]["Stadtteilname"]
                else:
                    po[d].append(p)
        else:
            print("error: ", w)
            return None

    print("Created ", len(po), " district lists")

    polyPlot = False
    mrg = []
    for p in po.keys(): # loop over all districts
        mp = Polygon([]) # initialize empty boundary polygon
        for pp in po[p]: # loop over all polygons
            mp = mp.union(pp)   # and merge them
        # finally, append the union as a geojson feature for this district
        mrg.append(geojson.Feature(
            properties={"Stadtteilnummer":p,
                        "Stadtteilname":ds[p]},
            geometry=mp))
        # optionally plot
        if polyPlot:
            plt.plot(*mp.exterior.xy)
            plt.show()

    # write to geojson file
    with open(Path("merged"+file), 'w', encoding="utf-8") as outfile:
        json.dump(geojson.FeatureCollection(features=mrg), outfile, indent=1) # with indent=2 we get line formatting
    outfile.close()
    return mrg

#################################

# open original baumkataster file
bf = Path("baum-ka.json")
if bf.is_file():
    with open(bf, "r", encoding='utf-8') as f:
        b = json.load(f)
        f.close()
else:
    print("No trees file")
    sys.exit()

bk = b.keys()
print("Keys: ", bk)

if not "features" in bk:
    print("No featuers")
    sys.exit()

t = b["features"]
print("Features: ", len(t))

#subset for test
#t = t[:1000]

trees = []
types = []
treeTypes = []
for tree in t:
    try:
        lt = tree["geometry"]["coordinates"][1]
        lg = tree["geometry"]["coordinates"][0]
        pdt =  tree["properties"]["ARTDEUT"]
        pl =  tree["properties"]["ARTLAT"]
        pg = tree["properties"]["BAUMGRUPPE"] != "Einzelbaum"
        trees.append((lt, lg, pdt, pl,pg))
        if not pl in types:
            types.append(pl) # helpr array to make indexing simpler
            treeTypes.append({"name":pl, "count":1})
        else:
            treeTypes[types.index(pl)]["count"] += 1
            #pass
    except:
        print("skipping: ", tree)
        pass

#save global value
globs["trees"] = len(trees)

# need a dictionary for the urls
urlDict = dict()
#try to read tree links
tf = Path("treeUrls.json")
if tf.is_file():
    with open(tf, "r", encoding='utf-8') as f:
        treeUrls = json.load(f)
        f.close()
    for t in treeUrls:
        urlDict[t["name"]] = t["url"]
    print("Urls read")
    print("urls: ", urlDict)

# sort trees by count
def typeKey(type):
    return type["count"]
treeTypes.sort(key=typeKey)
treeTypes.reverse() # put freqeunt trees in front
print("Number of types:", len(treeTypes))

try:
    with open(Path("treeCats.json"),"r") as f:
        treeCats = json.load(f)

    for tt in enumerate(treeTypes):
        if tt[1]["name"] in treeCats:
            treeTypes[tt[0]]["klam"] = treeCats[tt[1]["name"]]
        else:
            treeTypes[tt[0]]["klam"] = "0"

except:
    print("No or invalid treeCats file")
    sys.exit()


tf = Path("treeTypes.json")
with open(tf, "w", encoding='utf-8') as f:
    json.dump(treeTypes, f)
    f.close()
print("Treetypes written to ", tf)


#print("Types:", treeTypes, treeCounts)

# test: truncate
#trees = trees[:1000]


# either load a districts file
# or a "wahlbezirke" file and
# create the districts from it
useDistricts = False
if useDistricts:
    districts = loadDistricts("districts.json")
else:
    districts = loadElectRegions("landtagswahl_2016_wahlbezirke.geojson")

if districts == None:
    print("No districts file")
    sys.exit()

# sort districts by district number
def distId(item):
    return int(item["properties"]["Stadtteilnummer"])

districts.sort(key=distId)
#print("Sorted districts: ",districts)

# save global value
globs["districts"] = len(districts)

# note: coordinate order in trees and districts is reversed

# create points
pt = []
for t in trees:
    pt.append(Point(t[1], t[0]))
print("Created ", len(pt), " points")

# create polygons
po = []
for d in districts:
    print(d["properties"]["Stadtteilname"])
    # create oject for area calculation
    obj = {'type':'Polygon', 'coordinates':d["geometry"]["coordinates"]}
    # coordinates have one extra diemnsion ...
    c = d["geometry"]["coordinates"][0]
    p = Polygon(c)
    # save global value
    po.append({"polygon":p, "area":area(obj), "bounds":p.bounds})
    globs["area"] += area(obj)
    # create district array
print("Created ", len(po), " polygons")

print("Sorting trees to districts ...")
#annotated tree list
anTrees = []
#misTrees = []
#misPoints = []
# also computer trees per districts
distTrees = dict()

def pt2district(points, offset = False):
    # for every point check in which district it is
    misPoints = []
    misTrees = []
    for ti in range(len(points)):
        for di in range (len(po)):
            pnt = points[ti]
            if offset:
                # correct point coordinates towards center
                dx = pnt.x - CENTER["lon"]
                dy = pnt.y - CENTER["lat"]
                pnt = Point((pnt.x - .4 * dx,pnt.y - .4 * dy))
                    
            if pnt.within(po[di]["polygon"]):
                t = []
                for tt in trees[ti][:4]: # iterate over tree fields, leave out baumgruppe
                    t.append(tt)
                dn = int(districts[di]["properties"]["Stadtteilnummer"])
                t.append(dn)
                t.append(districts[di]["properties"]["Stadtteilname"])
                if distTrees.get(dn) == None:
                    distTrees[dn] = 1
                else:
                    distTrees[dn] += 1
                # we have the baumgruppe boolean as last field now
                # need to load explicitly ..
                u = urlDict.get(trees[ti][3]) # try to read url. name is already in last tt
                if u == None:
                    t.append("")
                else:
                    t.append(u)
                # check if we have the klam category in the types. latin name is in tt[3]
                if trees[ti][3] in treeCats:
                    t.append(treeCats[trees[ti][3]])
                else:
                    t.append("")
                
                anTrees.append(t)
                break

            elif di == len(po)-1:
                #print("Point ",ti," not on map: ",points[ti])
                misPoints.append(pt[ti])

    return misPoints

misPoints = pt2district(pt)
print("Missed points 1:", len(misPoints))

if len(misPoints) > 0:
    misPoints = pt2district(misPoints,True)

print("Missed points 2:", len(misPoints))
    

# function to sort trees by district number (item 4)
def districtKey(item):
    return item[4]

anTrees.sort(key=districtKey)

# write annotated tree file
af = Path("trees.json")
with open(af, "w", encoding='utf-8') as f:
    json.dump(anTrees, f)
    f.close()
print("Annotated trees saved to ", af)


# read bevölkerung
bevUrl = "https://transparenz.karlsruhe.de/dataset/74561f6a-4783-4d70-b86a-008deec09441/resource/71ef348f-0f5b-46a0-8250-e87aae9f91bd/download/bevolkerung-wohnberechtigte-bevolkerung.csv"
try:
    bev = pd.read_csv(bevUrl)
    bev = bev[bev.Jahr == 2020]
    bev.reset_index(drop=True,inplace=True)
    bev.index += 1
    globs["pop"] = int(bev.Wohnberechtigte.sum())
except:
    print("Reading population failed")
    sys.exit()

# metrics: population/km² [100000], tree/km² [1000], population/tree
# ranges should be between 1..10
# area in km²
globs["area"] = round(globs["area"]/1000000, 2)
print("Global values:", globs)
# compute mean values
means = {}
means["area"] = round(globs["area"]/len(districts), 2)
means["pop"] = round(globs["pop"]/len(districts), 2)
means["trees"] = round(globs["trees"]/len(districts), 2)
print("Means values:", means)

# area grünwettersbach should be around 6037193.23 m², 6km²
# computed area is 6037193
# also write district file for leaflet with reversed coordinates
dl = []
for di in range(len(districts)):
    d = districts[di]
    c = d["geometry"]["coordinates"][0]
    cc = []
    # reverse coordinates
    for ccc in c:
        cc.append([ccc[1], ccc[0]])
    dd = {"id":d["properties"]["Stadtteilnummer"], "name":d["properties"]["Stadtteilname"]}
    dd["bounds"] = po[di]["bounds"]
    dd["center"] = [(po[di]["bounds"][0]+po[di]["bounds"][2])/2,(po[di]["bounds"][1]+po[di]["bounds"][3])/2]
    dd["area"] = po[di]["area"]
    dd["population"] = int(bev.loc[int(d["properties"]["Stadtteilnummer"])]["Wohnberechtigte"])
    ## dd["population"] = pp[int(d["properties"]["Stadtteilnummer"])-1]["Wohnberechtigte"]
    dd["coordinates"] = cc
    dd["trees"] = distTrees[int(d["properties"]["Stadtteilnummer"])]
    dd["means"] = means
    dl.append(dd)

df = Path("districtsLeaf.json")
with open(df, "w", encoding='utf-8') as f:
    json.dump(dl, f)
    f.close()
print("Leaflet districts saved to ", df)
