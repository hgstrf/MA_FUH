import networkx as nx
import csv

G = nx.Graph()
with open('nodes.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)  
    for row in reader:
        G.add_node(row['name'], label=row['labels'])  
with open('relationships.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # add edge if both nodes exist in the graph to avoid errors
        if row['source'] in G and row['target'] in G:
            G.add_edge(row['source'], row['target'], relationship=row['type'])

nx.write_gexf(G, "graph.gexf")
