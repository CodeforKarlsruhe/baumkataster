import geopandas as gp

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

