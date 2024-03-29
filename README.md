# Erweiterung von Autoren- und Co-Zitationsgraphen um inhaltliche Aspekte
Dieses Repository enthält den Code zur schriftlichen Ausarbeitung. Dies beinhaltet in allererster Linie den Hauptteil der Arbeit, also den Gesamtworkflow, sowie alle weiteren, relevanten Schritte und diverse Auswertungen und Statistiken. Zu beachten ist die Reihenfolge der Codeausführung, nähere Details sind im Folgenden an relevanten Stellen gelistet.

## Erklärung des Codes der einzelnen Schritte
Jeder Schritt wird im Folgenden genauer erläutert. Relevant hierbei ist, dass alle Schritte nacheinander befolgt werden sollen. Dies geht auch aus der Dateienbenennung der einzelnen Skripte hervor. Zusätzlich zu den im Folgenden gelieferten Informationen sind auch die jeweiligen readme.txt-Dateien (falls vorhanden) der Unterordner von Relevanz und sollten gelesen und befolgt werden.

## Schritt 1: Akquise der Dokumente
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

## Schritt 2: Preprocessing
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
- *.gexf erlaubt auch Verwendung in dedizierten Graphenanalyseapplikationen

#### functions.py und functions_analysis.py
- enthalten notwendige Funktionen
- GROBID-Einstellungen wie Port können hier verändert werden



## Schritt 3: TRCs
Im dritten Schritt werden die TRC-Kandidaten berechnet und bestimmt, sowie Analysen und weitere Verarbeitungsschritte vorgenommen. Die Berechnung selbst erfolgt mit der Hagen-NLP-Toolbox, benötigt wird hier der Output der "centroid candidates" in txt-Form sowie der Graphenoutput (databases & transactions) im Ordner des lokalen Neo4j Server.

#### 3.1_analyze_centroid_candidates.py
- analysiert Ergebnisse aus der TRC-Berechnung
- visualisiert Ergebnisse in Graphenform
- gibt Statistiken in Konsole aus

#### 3.2_coocc_from_neo4j_to_csv und 3.2_coocc_from_csv_to_gexf.py
- Hilfsskripte, welche den Neo4j-Graphen in das *.gexf-Format umwandeln
- Erlaubt weitere Analyse mit Python oder Graphenanalyseapplikationen
- Port des lokalen Neo4j-Servers: 7687, kann angepasst werden


## Schritt 4: Clustering
Im vierten Schritt werden verschiedenste Clusteringalgorithmen auf die zuvor prozessierten Daten angewandt. Im Anschluss werden diese untersucht und eine Qualitätsbewertung vorgenommen, soweit Statistiken errechnet und Ergebnisse visualisiert.

#### 4.1_kmeans.py
- sollte immer zuerste ausgeführt werden, da hier die Ordnerstrukturen erzeugt werden
- wendet k-Means auf Zentroidkandidaten an

#### Schritte 4.2 bis 4.4
- enthalten Code zur Prozessierung der einzelnen Clusteralgorithmen bzw. deren Matching
- Ergebnisse werden nach Matching gemeinsam in der durch k-Means erstellten Ordner- und Datenstruktur gespeichert
- Reihenfolge sollte beachtet werden, jedoch nicht zwingend erforderlich

#### 4.5_map_clustering_and_TRCs.py
- matcht die Ergebnisse des Clusterings zu den TRC-Termen
- wird für weitere Analysen benötigt
- Ergebnisse werden in txt-Dateistruktur abgelegt

#### 4.6_quality_analysis_distances_within_clusters.py und 4.6_quality_analysis_statistics_and_visualization.py
- berechnet, prozessiert und visualisiert Ergebnisse der Analyse
- für Distanzberechnung wird erneut auf Neo4j zurückgegriffen, auch hier wird Port 7687 verwendet, auch dieser kann angepasst werden


## Schritt 5: Clustering für Graphen
Im fünften und letzten Schritt werden die Ergebnisse des Clusterings auf die tatsächlichen Graphen angewandt, also eine inhaltliche Erweiterung durchgeführt. Dies ist der letzte Schritt, und benötigt daher die folgenden Unterordner, die in vorhergehenden Schritten erzeugt wurden:
- publications_directory = './input/GrobidOutput/'
- co_citations_directory = './input/co_citation_input_50_docs/'
- centroid_directory = './input/centroidcandidates/'
- seqclu_directory = './input/seqclu/'

Verwendet hierfür wird nachfolgender Code.

#### 5_extend_Graphs_by_topic_clustering.py
- verwendet Autoreninformationen- oder Co-Zitationsinformationen
- verwendet Clusterergebnisse
- erzeugt mehrere Datentabellen mit Metainformationen
- erzeugt Graphenstruktur mit thematischer Komponente
- analysiert Ergebnisse und gibt diese aus
- genauere Informationen zur Theorie in Ausarbeitung, Kapitel "Anwendung auf Autoren- und Co-Zitationsgraphen"
