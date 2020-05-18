import geopandas as gp

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




baumfile = "baumfile.json"
baumtable = "baumtable.csv"

b = gp.read_file("https://geoportal.karlsruhe.de/server/rest/services/Fachplaene/Baumkataster/MapServer/1/query?where=ARTDEUT+IS+NOT+NULL&outFields=ARTDEUT%2CARTLAT%2CBAUMGRUPPE%2CLFDNR%2CLFDBNR&returnGeometry=true&f=geojson")

# separate points into x,y
b["X"] = b["geometry"].x
b["Y"] = b["geometry"].y

b.to_csv(baumtable,index=False)
print("Tree table written to ",baumtable)

with open(baumfile,"w") as f:
    f.write(b.to_json())

print("Trees written to ",baumfile)

groups = b.loc[b["BAUMGRUPPE"] == "Baumgruppe"]
singles = b.loc[b["BAUMGRUPPE"] == "Einzelbaum"]


print("Groups: ", len(groups))
print("Singles: ", len(singles))

