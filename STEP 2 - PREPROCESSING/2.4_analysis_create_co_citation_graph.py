import os
from collections import defaultdict
import networkx as nx
from tqdm import tqdm

def read_citations(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file]

folder_path = './output/authors_citations'
# requires data in folder

co_citations = defaultdict(int)

files = [file for file in os.listdir(folder_path) if file.endswith('.txt')]

for file in tqdm(files, desc='Processing files'):
    authors_cited = read_citations(os.path.join(folder_path, file))
    # update the co-citations count
    for i in range(len(authors_cited)):
        for j in range(i+1, len(authors_cited)):
            co_citations[(authors_cited[i], authors_cited[j])] += 1
G = nx.Graph()

# progress (can take quite a long time if the document basis is large)
for (author1, author2), count in tqdm(co_citations.items(), desc='Building Graph'):
    G.add_edge(author1, author2, weight=count)

# export the graph to a GEXF file (for use in Gephi or somewhere else)
nx.write_gexf(G, "citation_graph.gexf")
print("Graph exported as GEXF file.")

# basic statistics
number_of_nodes = G.number_of_nodes()
number_of_edges = G.number_of_edges()
print("Number of Nodes:", number_of_nodes)
print("Number of Edges:", number_of_edges)
