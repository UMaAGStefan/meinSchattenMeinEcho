
# meinSchattenMeinEcho
Das Repository soll helfen Schall und Schattenberechnungen nach den LAI Hinweisen, sowie gemäß TA Lärm und ISO 9613-2 auszuführen und zu bewerten.

Neben der Berechnung und Bewertung, können auch möglich Schallkonzept erstellt und bewertet werden.

## Beschreibung
Die Berechnung der Schattenimmission erfolgt nach den "Hinweise zur Ermittlung und Beurteilung der optischen Immissionen von Windkraftanlagen Aktualisierung 2019" Stand 23.01.2020
Bei der Berechnung wird nur die astronomisch maximal mögliche Beschattungsdauer ermittelt.

Die Berechnung der Schallimmissionen wird auf Basis der DIN ISO 9613-2 durchgeführt.
Für bodennahen Quellen (hier Annahme kleiner 50 m ü.GOK) wird das "Alternativeverfahren" verwendet.
Für hochliegende Quellen (hier Annahme höher 50m ü. GOK) wird das "Interimsverfahren" verwendet.
Für das Interimsverfahren wird die Berechnung entsprechnd der LAI Hinweise und der "Dokumentation zur 
Schallausbreitung – Interimsverfahren zur Prognose der Geräuschimmissionen von Windkraftanlagen, Fassung 2015-05.1“ angepasst.

Darüber hinaus können Schallkonzepte nach bestimmten Strategien erstellt werden. 
Mit der Strategie "FortePiano" wird die geplante Windkraftanlage in der Lautstärke reduziert, die den größten Beitrag auf 
den am höchsten überschrittenen Immissionspunkt hat. 
Das wird so oft wiederholt, bis an allen Immissionspunkte der Richtwerteingehalten wird.
Desweiteren kann man von einem bestehenden Schallkonzept eine Variation an Kombinatione unter den geplanten Windkraftanlagen bewerten lassen
und die Kombinationen mit der höchsten Nennlast ausgeben lassen ("ExtraRundeSchallModes").
## Funktionen
### shadow.py (Schatten)
Es werden folgende Annahme zur Bestimmung des Schattenwurfs einer Windkraftanlage angenommen:
- Die Windrichtung entspricht dem Azimutwinkel der Sonne, die Rotorkreisfläche steht immer senkrecht zur
Einfallsrichtung der direkten Sonneneinstrahlung. 
- Der Schattenwurf wird nur für Sonnenstände über 3° ermittelt.
- Der Beitrag einer Windkraftanlage wird nur berücksichtigt, wenn der Schattenimmissionspunkt im Beschattungsbereich der 
Windkraftanlage liegt.
- Der Beschattungsbereich ergibt sich aus dem Abstand zur Windkraftanlage, in welchem die Sonnenfläche gerade zu 20 % 
durch ein Rotorblatt verdeckt wird. 
- Da die Blatttiefe nicht über den gesamten Flügel konstant ist, sondern zur Rotorblattspitze hin abnimmt, wird 
ersatzweise ein rechteckiges Rotorblatt mit einer mittleren Blatttiefe ermittelt und der entsprechende Beschattungsbereich bestimmt.
### noise.py (Schall)
Hier liegen mehrer Funktionen, es gibt eine Funktion für die Berechnung der Immissionen, die Berechnungsmethode 
("Alternatives- oder Interimsverfahren) wird automatisch je nach Höhe des Emittenten gewählt.
Weiterhin findet hier auch die Bewertung der ermittelten Immissionen statt.
Auch die Schallkonzepte können hier abgerufen werden.
## Anforderungen-Python [Version]
Requirement.txt steht noch aus
## Installation1.[Schritte zur Installation]
Das Repository kann geklont werden

```git clone https://github.com/UMaAGStefan/meinSchattenMeinEcho ```

## Verwendung
1. Vorbereiten der Eingangsdaten in Excel
2. Ausführung des Python scripts main.py
## Beispiele```python
# Beispielcode hier
