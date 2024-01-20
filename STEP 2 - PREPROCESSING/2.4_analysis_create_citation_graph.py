import os
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
from collections import defaultdict
from tqdm import tqdm

def read_author_data(co_citation_folder):
    co_citation_relationships = defaultdict(lambda: defaultdict(int))

    for pub_folder in tqdm(os.listdir(co_citation_folder), desc="Processing Pub Folders"):  
        pub_path = os.path.join(co_citation_folder, pub_folder)
        if os.path.isdir(pub_path):
            cited_documents = []

            for file in os.listdir(pub_path):
                with open(os.path.join(pub_path, file), 'r', encoding='utf-8') as f:
                    authors = f.read().splitlines()
                    cited_documents.append(set(authors))

            for doc1, doc2 in combinations(cited_documents, 2):
                for author1 in doc1:
                    for author2 in doc2:
                        co_citation_relationships[author1][author2] += 1
                        co_citation_relationships[author2][author1] += 1

    return co_citation_relationships

def build_co_citation_graph(co_citation_data):
    G = nx.Graph()
    pbar = tqdm(co_citation_data.items(), desc="Building Citation Graph") 

    for author, co_authors in pbar:
        for co_author, weight in co_authors.items():
            if author != co_author:
                G.add_edge(author, co_author, weight=weight)

    return G

def visualize_graph(G):
    plt.figure(figsize=(15, 15))
    pos = nx.spring_layout(G)  

    # edge width based on weight, can be changed
    edge_widths = [G[u][v]['weight'] * 0.5 for u, v in G.edges()]  

    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=700)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=12)
    plt.title("Citation Graph")
    plt.show()

co_citation_folder = './output/co_citation_input/'
#co_citation_folder = './output/test/'
co_citation_data = read_author_data(co_citation_folder)
G = build_co_citation_graph(co_citation_data)


# export graph for gephi or other tools
gexf_filename = 'citation_graph.gexf'
nx.write_gexf(G, gexf_filename)
print(f"The graph has been saved as {gexf_filename}.")

# basic statistics
number_of_nodes = G.number_of_nodes()
number_of_edges = G.number_of_edges()
print("Number of Nodes:", number_of_nodes)
print("Number of Edges:", number_of_edges)


# visu
visualize_graph(G)
