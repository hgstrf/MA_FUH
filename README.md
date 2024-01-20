# Erweiterung von Autoren- und Co-Zitationsgraphen um inhaltliche Aspekte
- Code zur schriftlichen Ausarbeitung
- Enthält Hauptteil der Aufgabe sowie alle relevanten Schritte
- Reihenfolge der Codeausführung beachten

## Erklärung des Codes der einzelnen Schritte
Jeder Schritt wird im Folgenden genauer erläutert. Relevant hierbei ist, dass alle Schritte nacheinander befolgt werden sollen. Dies geht auch aus der Dateienbenennung der einzelnen Skripte hervor.

### Schritt 1: Akquise der Dokumente
Im ersten Schritt werden PDF-Dokumente akquiriert. Dieser Schritt ist optional, und kann durch eine lokale Dokumentensammlung ersetzt werden.

#### 1.1_crawler_GUI.py
- enthält Code des Webcrawlers
- durchsucht systematisch Internet beginnend von Startlink
- sucht PDF-Dateien und lädt diese herunter

#### 1.2_API_downloader_GUI.py
- enthält Code des API-Downloaders
- sucht und lädt wissenschaftliche Publikationen gezielt herunter
- angebunden an arXiv-API, kann aber einfach an jede andere API angebunden werden

#### 1.3_crawler_result_analysis.py
- enthält Code zur Visualisierung und Analyse der Ergebnisse
- nicht relevant für weitere Arbeitsschritte

### Schritt 2: Preprocessing
Schritt 2 dient dem Preprocessing der Daten. In erster Linie werden die akquirierten Dokumente klassifiziert und für die Berechnung der TRCs im nächsten Schritt aufbereitet. Verwendet wird heirfür ein lokaler GROBID-Webserver, der auf Port 8070 läuft. Angepasst werden kann dieser in der 'functions.py'-Datei

#### 2.1_GROBID_processing.py
- enthät Gesamtcode zur Klassifizierung und Prozessierung der PDFs mittels GROBID wie in Ausarbeitung beschrieben
- benötigt wird input-Ordner './input/docs', anpassbar über Code
- Outputordner werden automatisiert erstellt
  
#### 2.2_analysis_process_XML_files.py
- enthält Code zur Prozessierung der von GROBID erzeugten XML-Dateien
- verarbeitet XML-Dateien, indem relevante Daten wie Autoreninformationen extrahiert werden
- speichert Ergebnisse in txt-Dateistruktur

#### 2.3_analysis_citations.py
- extrahiert und analysiert Zitationsbeziehungen
- speichert Ergebnisse im erzeugten Ordner 'authors_citations'

#### 2.4_analysis_create_citation_graph.py bzw. 2.4_analysis_create_co_citation_graph.py
- erzeugt und visualisiert Graphenstruktur aus zuvor extrahierten Informationen
- speichern Graphen im *.gexf-Dateiformat, um spätere Verwendung zu gewährleisten
- *.gexf erlaubt auch Verwendung in dedizierten Graphenanalyseapplicationen

#### functions.py und functions_analysis.py
- enthalten notwendige Funktionen
- GROBID-Einstellungen wie Port können hier verändert werden
