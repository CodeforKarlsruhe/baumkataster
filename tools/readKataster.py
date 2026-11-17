import geopandas as gp
import pandas as pd
from datetime import date

# documentation for the (new, hosted) kataster service is here:
# https://geoportal.karlsruhe.de/ags04/rest/services/Hosted/Baumkataster/FeatureServer/2

##Layer: Bäume (Zoomstufe 16 bis 18) (ID: 2)
##Name: Bäume (Zoomstufe 16 bis 18)
##Display Field: artdeut
##Type: Feature Layer
##Geometry Type: esriGeometryPoint
##Supported Query Formats: JSON, PBF, geoJSON
##HTML Popup Type: esriServerHTMLPopupTypeAsHTMLText
##
##Fields:
##
##    objectid ( type: esriFieldTypeOID , alias: OBJECTID )
##    lfdbnr ( type: esriFieldTypeInteger , alias: LFDBNR )
##    lfdnr ( type: esriFieldTypeInteger , alias: LFDNR )
##    artdeut ( type: esriFieldTypeString , alias: ARTDEUT , length: 255 )
##    artlat ( type: esriFieldTypeString , alias: ARTLAT , length: 255 )
##    baumart_allgemein ( type: esriFieldTypeString , alias: Baumart allgemein , length: 255 )
##    baumgruppe ( type: esriFieldTypeString , alias: BAUMGRUPPE , length: 255 )
##    stadtteil ( type: esriFieldTypeString , alias: Stadtteil , length: 255 )
##    html ( type: esriFieldTypeString , alias: HTML , length: 4000 )
##
##The layer has maxRecordCount = 2000, so queries must be paginated with
##resultOffset/resultRecordCount (orderByFields=objectid keeps pages stable).
##The server answers with "properties": {"exceededTransferLimit": true} as
##long as more records are available.

# old (dead) servers, kept for reference:
# https://geoportal.karlsruhe.de/server/rest/services/Fachplaene/Baumkataster/MapServer/1/query?...
#   returned ~10k trees (server-side truncation) with UPPERCASE field names
# https://geoportal.karlsruhe.de/ags04/rest/services/Hosted/Baumkataster/FeatureServer/2/query?...
#   without resultOffset this is truncated to the server maximum as well

baumfile = f"baumfile-{date.today():%Y%m%d}.json"
baumtable = f"baumtable-{date.today():%Y%m%d}.csv"

BASE_URL = (
    "https://geoportal.karlsruhe.de/ags04/rest/services/Hosted/"
    "Baumkataster/FeatureServer/2/query"
)
# NOTE: no "html" field. it is redundant (contains only baumart_allgemein and
# zuordnung) and would blow up both download size and the csv table.
OUT_FIELDS = "objectid,lfdbnr,lfdnr,artdeut,artlat,baumart_allgemein,baumgruppe,stadtteil"
PAGE_SIZE = 2000  # must not exceed the layer's maxRecordCount
OFFSET_LIMIT = 1000000  # safety cap against runaway loops

offset = 0
all_data = []

while True:
    url = (
        f"{BASE_URL}?where=1%3D1&outFields={OUT_FIELDS}"
        f"&resultOffset={offset}&resultRecordCount={PAGE_SIZE}"
        f"&orderByFields=objectid&returnGeometry=true&f=geojson"
    )
    print("Reading offset", offset, url)

    # the server is occasionally slow/failing; retry a few times
    data = None
    for attempt in range(5):
        try:
            data = gp.read_file(url)
            break
        except Exception as e:
            print("  attempt", attempt + 1, "failed:", e)
    if data is None:
        raise RuntimeError(f"giving up at offset {offset}")

    if data.empty:
        break

    print("Read ", len(data))
    all_data.append(data)
    offset += len(data)

    if len(data) < PAGE_SIZE:
        # last (partial) page -> we have everything
        break
    if offset > OFFSET_LIMIT:
        print("offset limit reached, stopping")
        break

b = gp.GeoDataFrame(pd.concat(all_data, ignore_index=True))

# the new FeatureServer returns lowercase field names, the old MapServer
# (and thus baum-ka.json / treeDistrictMap.py) used UPPERCASE names.
# rename so the output files stay compatible.
b = b.rename(columns={c: c.upper() for c in b.columns if c != b.geometry.name})

print(len(b), b.keys())

# separate points into x,y
b["X"] = b["geometry"].x
b["Y"] = b["geometry"].y

b.to_csv(baumtable, index=False)
print("Tree table written to ", baumtable)

with open(baumfile, "w") as f:
    f.write(b.to_json())

print("Trees written to ", baumfile)

groups = b.loc[b["BAUMGRUPPE"] == "Baumgruppe"]
singles = b.loc[b["BAUMGRUPPE"] == "Einzelbaum"]

n_artdeut_null = int(b["ARTDEUT"].isna().sum())
n_artlat_null = int(b["ARTLAT"].isna().sum())
print("Trees without ARTDEUT:", n_artdeut_null)
print("Trees without ARTLAT :", n_artlat_null)

print("Groups: ", len(groups))
print("Singles: ", len(singles))
print("Total: ", len(singles) + len(groups))
