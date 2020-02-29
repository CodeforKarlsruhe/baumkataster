# -*- coding: utf-8 -*-
"""create newletter html from templates and input csv files """

import os # builtin
import sys # builtin
import csv # builtin
import locale # builtin
from pathlib import Path,PurePath # pip install pathlib
import json
import textdistance


locale.setlocale(locale.LC_ALL,"de_DE.UTF-8")


klamIn = "klam-table.csv"
klamOut = "klam.csv"

trees = []
# fields: Id	Size	LatinName	GermanName	Category
print("using file: ",str(Path(klamIn)))
with open(Path(klamIn),newline='') as csvfile:
    # create reader
    r = csv.DictReader(csvfile,delimiter=",",quotechar="\"",quoting=csv.QUOTE_MINIMAL)
    for row in r:
        #print(row)
        item = {}
        for rr in row:
            if "Name" in rr:
                item.update({rr:row[rr].strip()})
            elif rr == "Size" or rr == "Category":
                item.update({rr:row[rr]})
        if item["Size"] == "":
            continue # skip empty lines
        trees.append(item)

    csvfile.close()

#articleFields = ["headline","img_link","img_alt","text","next_link","next_label"]

# create array with all latin names and write all trees
types = []

with open(Path(klamOut),"w") as fo:
    outfields = trees[0].keys()
    print(outfields)
    writer = csv.DictWriter(fo, quoting=csv.QUOTE_NONNUMERIC,delimiter=',',quotechar='"', fieldnames=outfields)
    writer.writeheader()
    for t in trees:
        writer.writerow(t)
        prop = {}
        prop.update({"name":t["LatinName"],"category":t["Category"]})
        types.append(prop)

fo.close()


# read tree types
df = Path("treeTypes.json")
with open(df, "r", encoding='utf-8') as f:
    treesKa = json.load(f)
    f.close()

o = 0 #options
for t in enumerate(treesKa):
    # try to match
    treesKa[t[0]]["klam"] = "0" # default unset
    for ty in types:
        # levenshtein takes longer, but gives better results
        #d = textdistance.hamming.normalized_similarity(t[1]["name"], ty["name"])
        d = textdistance.levenshtein.normalized_similarity(t[1]["name"], ty["name"])
        if d > .55:
            print("option: ",t[1]["name"],":",ty["name"])
            o += 1
            treesKa[t[0]]["klam"] = ty["category"]
            break


print("Total: ",len(treesKa),", options: ",o)

# write updated trees types
df = Path("treeTypesKlam.json")
with open(df, "w", encoding='utf-8') as f:
    json.dump(treesKa,f)
    f.close()


