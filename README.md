# Erweiterung von Autoren- und Co-Zitationsgraphen um inhaltliche Aspekte
- Code zur schriftlichen Ausarbeitung
- Enthält Hauptteil der Aufgabe sowie alle relevanten Schritte
- Reihenfolge der Codeausführung beachten

## Übersicht der einzelnen Schritte
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
