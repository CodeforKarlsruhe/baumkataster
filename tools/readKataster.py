import geopandas as gp
import pandas as pd

# documentation for reading kataster file is here:
# https://geoportal.karlsruhe.de/server/rest/services/Fachplaene/Baumkataster/MapServer/1

##Layer: Bäume (Zoomstufe 16 bis 18) (ID: 1)
##Name: Bäume (Zoomstufe 16 bis 18)
##Display Field: ARTDEUT
##Type: Feature Layer
##Geometry Type: esriGeometryPoint
##Supported Query Formats: JSON, AMF, geoJSON
##HTML Popup Type: esriServerHTMLPopupTypeAsHTMLText

##Fields:
##
##    OBJECTID ( type: esriFieldTypeOID , alias: OBJECTID )
##    LFDBNR ( type: esriFieldTypeInteger , alias: LFDBNR )
##    LFDNR ( type: esriFieldTypeInteger , alias: LFDNR )
##    ARTDEUT ( type: esriFieldTypeString , alias: ARTDEUT , length: 255 )
##    ARTLAT ( type: esriFieldTypeString , alias: ARTLAT , length: 100 )
##    BAUMGRUPPE ( type: esriFieldTypeString , alias: BAUMGRUPPE , length: 100 )
##    HTML ( type: esriFieldTypeString , alias: HTML , length: 4000 )
##    SHAPE ( type: esriFieldTypeGeometry , alias: SHAPE )
##




baumfile = "baumfile-20250311.json"
baumtable = "baumtable-20250311.csv"

# new 2024
url = "https://geoportal.karlsruhe.de/server/rest/services/Fachplaene/Baumkataster/MapServer/1/query?where=STADTTEIL+IS+NOT+NULL&outFields=LFDBNR%2CARTDEUT%2CARTLAT%2CBAUMART_ALLGEMEIN%2CBAUMGRUPPE%2CSTADTTEIL&returnGeometry=true&f=geojson"

url = "https://geoportal.karlsruhe.de/ags04/rest/services/Hosted/Baumkataster/FeatureServer/2/query?where=lfdbnr+IS+NOT+NULL&outFields=artdeut%2Cartlat%2Cbaumgruppe%2Clfdnr%2Clfdbnr%2Cbaumart_allgemein&returnGeometry=true&f=geojson"

offset = 0
all_data = []

while True:
    print("Reading offset ",offset)
    url = f"https://geoportal.karlsruhe.de/ags04/rest/services/Hosted/Baumkataster/FeatureServer/2/query?where=1%3D1&outFields=*&resultOffset={str(offset)}&resultRecordCount=1000&orderByFields=objectid&returnGeometry=true&f=geojson"
    print("Reading offset ",offset,url)
    data = gp.read_file(url)
    
    if data.empty:
        break
    
    print("Read ",len(data))
    all_data.append(data)
    offset += 1000
    
    if offset > 200000:
        break

b = gp.GeoDataFrame(pd.concat(all_data, ignore_index=True))

print(len(b), b.keys())

# separate points into x,y
b["X"] = b["geometry"].x
b["Y"] = b["geometry"].y

b.to_csv(baumtable,index=False)
print("Tree table written to ",baumtable)

with open(baumfile,"w") as f:
    f.write(b.to_json())

print("Trees written to ",baumfile)

groups = b.loc[b["BAUMGRUPPE".lower()] == "Baumgruppe"]
singles = b.loc[b["BAUMGRUPPE".lower()] == "Einzelbaum"]


print("Groups: ", len(groups))
print("Singles: ", len(singles))
print("Total: ", len(singles)+len(groups))

