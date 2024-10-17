
# meinSchattenMeinEcho
Das Repository soll helfen Schall und Schattenberechnungen nach den LAI Hinweisen, sowie gemäß TA Lärm und ISO 9613-2 auszuführen und zu bewerten. Es können auch möglich Schallkonzept erstellt werden.

## Beschreibung
### Schattenwurf
Die Berechnung der Schattenimmission erfolgt nach den "Hinweise zur Ermittlung und Beurteilung der optischen Immissionen von Windkraftanlagen Aktualisierung 2019" Stand 23.01.2020
Bei der Berechnung wird nur die astronomisch maximal mögliche Beschattungsdauer ermittelt.
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

### Schallimmissionen
Die Berechnung der Schallimmissionen wird auf Basis der DIN ISO 9613-2 durchgeführt.
Für bodennahen Quellen (hier Annahme kleiner 50 m ü. GOK) wird das "Alternativeverfahren" verwendet.
Für hochliegende Quellen (hier Annahme höher 50m ü. GOK) wird das "Interimsverfahren" verwendet.
Für das Interimsverfahren wird die Berechnung entsprechend der LAI Hinweise und der "Dokumentation zur 
Schallausbreitung – Interimsverfahren zur Prognose der Geräuschimmissionen von Windkraftanlagen, Fassung 2015-05.1“ angepasst.

Darüber hinaus können Schallkonzepte nach bestimmten Strategien erstellt werden. 
Mit der Strategie "FortePiano" wird die geplante Windkraftanlage in der Lautstärke reduziert, die den größten Beitrag auf 
den am höchsten überschrittenen Immissionspunkt hat. 
Das wird so oft wiederholt, bis an allen Immissionspunkte der Richtwerteingehalten wird.
Des weiteren kann man von einem bestehenden Schallkonzept eine Variation an Kombinationen unter den geplanten Windkraftanlagen bewerten lassen
und die Kombinationen mit der höchsten Nennlast ausgeben lassen ("ExtraRundeSchallModes").

## Installation
**Schritt 1:** Repository klonen

```git clone https://github.com/UMaAGStefan/meinSchattenMeinEcho ```

**Schritt 2:** Installation von Requirements

```pip install -r requirements.txt``` 

## Verwendung
**Schritt 1:** Vorbereiten der Eingangsdaten in Excel
- Beispiel Excel als Eingangsdatei gibts auf Anfrage oder als .pfd Export und dem Ordner Example

**Schritt 2:** Ausführung des Python scripts main.py - Ausgabe Datei wird erzeugt.

**Schritt 3:** Ergebnisse in der neuen Exceldatei begutachten-
