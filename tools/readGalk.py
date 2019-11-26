import tabula as tb
import pandas as pd
import csv

# pdf is at: http://strassenbaumliste.galk.de/sblistepdf.php

a = tb.read_pdf("galk_strassenbaumliste.pdf", multiple_tables=True, pages="all")
print(len(a))

for i in range(len(a)):
    if i == 0:
        df = pd.DataFrame(a[i])
    else:
        d = pd.DataFrame(a[i])
        df = df.append(d)


df = df.rename(columns = {"L1*" : "Lichtdurchlässigkeit",
                          "L2*" : "Lichtbedarf"})


with open("galk.csv", "w") as f:
    df.to_csv(f, index=False, sep=",", quoting=csv.QUOTE_NONNUMERIC,
              quotechar="\"", encoding="utf-8")
    f.close()


