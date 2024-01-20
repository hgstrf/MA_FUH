Benötigt werden folgende input-Ordner:

	[1] publications_directory = './input/GrobidOutput/'
	[2] co_citations_directory = './input/co_citation_input_50_docs/'
	[3] centroid_directory = './input/centroidcandidates/'
	[4] seqclu_directory = './input/seqclu/'

Diese werden alle durch die vorhergehenden Verarbeitungschritte erzeugt:
	[1] enthält Infos über die Publikationen, wie durch die GROBID-Analyse erzeugt
	[2] enthält die Co-Zitationsinformationen, wie durch das Preprocessing erzeugt. Im Code wurde eine Teilmenge aus 50 Dokumenten gewählt; tatsächlich kann dieser Ordnerpfad beliebig angepasst werden.
	[3] enthält die Zentroidkandidaten, die durch die Hagen-NLP-Toolbox erzeugt und exportiert wurden
	[4] enthält die Ergebnisse der Clusteringmethode, die zur weiteren Verarbeitung gewählt wurde (hier SeqClu, mehr Infos siehe Thesis)