# Baumkataster
Visualize communal trees

[Live webpage](https://codeforkarlsruhe.github.io/baumkataster/)

# Data source

Karlsruhe tree register (Baumkataster), served by the city geoportal as an
ArcGIS FeatureServer:

https://geoportal.karlsruhe.de/ags04/rest/services/Hosted/Baumkataster/FeatureServer/2

- ~131k trees (as of 11/2026), point geometries, EPSG:4326
- the server caps each query response at `maxRecordCount` (2000 features),
  so all tools paginate with `resultOffset`/`resultRecordCount` and
  `orderByFields=objectid`
- field names come back lowercase (`artdeut`, `baumgruppe`, ...); the old
  MapServer used UPPERCASE, so `readKataster.py` renames the columns to keep
  the output files compatible
- many trees (~28%) have no species (`artdeut`/`artlat` are null), mostly
  Obstbäume from the Liegenschaftsamt

# Tools

Python3 programs to compile the tree and district data files for the map
from the data sources. Dependencies:

    pip install geopandas pandas shapely area geojson textdistance

Run them inside `tools/`, in this order (there is a bootstrap step):

1. `readKataster.py`
   Downloads the full Baumkataster from the FeatureServer and writes
   `baumfile-YYYYMMDD.json` and `baumtable-YYYYMMDD.csv`.

2. `treeDistrictMap.py` (1st run)
   Reads `baum-ka.json` (copy/link your `baumfile-*.json` there) and writes
   `treeTypes.json`. It then stops, because `treeCats.json` does not exist
   yet — the script prints a hint.

3. `cleanKlam.py`
   Matches the tree types against the GALK street tree list
   (`klam-table.csv`) and writes `treeCats.json` (plus `klam.csv` and
   `treeTypesKlam.json`).

4. `treeDistrictMap.py` (2nd run)
   Completes the pipeline and writes `trees.json`, `districtsLeaf.json` and
   `treeTypes.json` (now with GALK categories).

Finally copy `trees.json`, `districtsLeaf.json` and `treeTypes.json` from
`tools/` into `assets/`.

# Web app

Static site (Leaflet), no build step. All asset URLs are hardcoded to the
GitHub Pages path `/baumkataster/`, so serve the *parent* directory of the
repository for a local preview:

    ln -s $(pwd)/baumkataster-repo /tmp/opencode/baumkataster  # adjust to your layout
    python3 -m http.server 8000 --directory /tmp/opencode

then open http://localhost:8000/baumkataster/

# Note
Baumkataster has tree groups. check for field "BAUMGRUPPE".
Also read LFDBNR and LFDNR
