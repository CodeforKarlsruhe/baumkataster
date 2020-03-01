<!DOCTYPE html>
<html><head>
<meta http-equiv="content-type" content="text/html; charset=UTF-8">
	
	<title>Info zum Baumkataster Karlsruhe</title>

	<meta charset="utf-8"></meta>

    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    </meta>

</head>
<body>



# Visualisierung des Baumkatasters der Stadt Karlsruhe
## Basisdaten
Die Daten des Karlsruher Baumkatatsters enthalten Standort und Namen der städtischen Bäume. Weitere Informationen wie
Alter, Größe oder eine eindeutige ID sind nicht verfügbar. Die Datei kann über das Transparenzportal unter [https://transparenz.karlsruhe.de/dataset/fachplane-baumkataster](https://transparenz.karlsruhe.de/dataset/fachplane-baumkataster) abgerufen werden. Nach dem Laden der Karten kann ein einzelner Stadtteil zur Ansicht ausgewählt werden (Achtung, die Auswahl "Alle" braucht sehr viel Rechenzeit, da alle 85000 Bäume verarbeitet werden müssen).

Zur Darstellung werden weitere Daten des Transparenzportals verwendet:
  * [Bevölkerungsdaten](https://transparenz.karlsruhe.de/dataset/bevolkerung/resource/71ef348f-0f5b-46a0-8250-e87aae9f91bd)
  * [Stadtteile](https://transparenz.karlsruhe.de/dataset/landtagswahl-2016/resource/a16d5625-4407-427b-9bc2-b5ce738d283c)

## Verarbeitung
In einem Vorverarbeitungsschritt werden die Bäume den einzelnen Stadtteilen zugeordnet und es können weitere 
Daten hinzugefügt werden, zum Beispiel die Klassifizierung nach [KLAM](https://www.die-gruene-stadt.de/klimaartenmatrix-stadtbaeume.pdfx) oder ein Link zu [Wikidata](https://de.wikipedia.org/wiki/Baum).

Die KLAM Klassifizierung wird bei den einzelnen Bäumen farbkodiert dargestellt, der vordere Index ergibt Grün, Gelb, Blau, Rot für 1,2,3,4. Der hintere Index liefert die Helligkeit (1: hell - 4: dunkel).

In der Overlay-Grafik werden Kennzahlen des Stadtteils Bevölkerung, Fläche und Baumzahl angezeigt, absolut und in Relation zum Mittelwert.

## Credits
[OK Lab Karlsruhe](https://ok-lab-karlsruhe.de)
![](https://codefor-karlsruhe.de/img/CfKA%20Hexagon%203d.svg)


</body>
</html>




  
