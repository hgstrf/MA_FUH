import os
import pandas as pd
from tqdm import tqdm
from collections import defaultdict
from itertools import combinations
import networkx as nx
import matplotlib.pyplot as plt

# Datentabelle 1, Autorenhraphen
def create_authors_table(directory):
    data = {'Filename': [], 'Author': []}
    for filename in tqdm(os.listdir(directory), desc='Processing authors'):
        if filename.endswith('_authors.txt'):
            adjusted_filename = filename.replace('_authors.txt', '')
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
                authors = file.read().splitlines()
                for author in authors:
                    data['Filename'].append(adjusted_filename)
                    data['Author'].append(author)
    return pd.DataFrame(data)

# Datentabelle 1, Co-Zitationsgraphen
def create_co_citation_table(base_folder):
    co_citation_data = defaultdict(lambda: defaultdict(int))
    data = {'Filename': [], 'Author1': [], 'Author2': [], 'Co-citations': []}

    for publication in tqdm(os.listdir(base_folder), desc="Processing Publications"):
        publication_path = os.path.join(base_folder, publication)
        if os.path.isdir(publication_path):
            cited_authors = []

            for file in os.listdir(publication_path):
                with open(os.path.join(publication_path, file), 'r', encoding='utf-8') as f:
                    authors = f.read().splitlines()
                    cited_authors.append(set(authors))

            for author_set1, author_set2 in combinations(cited_authors, 2):
                for author1 in author_set1:
                    for author2 in author_set2:
                        co_citation_data[(author1, author2)][publication] += 1

    for (author1, author2), publications in co_citation_data.items():
        for publication, count in publications.items():
            data['Filename'].append(publication)
            data['Author1'].append(author1)
            data['Author2'].append(author2)
            data['Co-citations'].append(count)

    return pd.DataFrame(data)


# Datentabelle 2
def create_centroid_table(centroid_directory):
    centroid_data = {'Filename': [], 'FirstCandidate': []}
    for filename in tqdm(os.listdir(centroid_directory), desc='Processing centroids'):
        with open(os.path.join(centroid_directory, filename), 'r', encoding='utf-8') as file:
            content = file.read().replace("Centroid candidate data sorted: ", "")
            first_candidate = content.split(',')[0].split('=')[0].strip('{')
            adjusted_filename = filename.replace('centroid_candidates_sorted_', '').split('_full_text.txt.txt.s.txt')[0]
            centroid_data['Filename'].append(adjusted_filename)
            centroid_data['FirstCandidate'].append(first_candidate)
    return pd.DataFrame(centroid_data)

# Datentabelle 3
def create_seqclu_table(seqclu_directory):
    seqclu_data = {'ClusterNumber': [], 'Filename': [], 'TRC': []}
    for filename in tqdm(os.listdir(seqclu_directory), desc='Processing seqclu'):
        cluster_number = filename.split('.txt')[0]
        with open(os.path.join(seqclu_directory, filename), 'r', encoding='utf-8') as file:
            for line in file:
                file_name, trc = line.strip().split(': ')
                adjusted_filename = file_name.split('_full_text.txt.txt.s')[0]
                seqclu_data['ClusterNumber'].append(cluster_number)
                seqclu_data['Filename'].append(adjusted_filename)
                seqclu_data['TRC'].append(trc)
    return pd.DataFrame(seqclu_data)

# directories
publications_directory = './input/GrobidOutput/'
co_citations_directory = './input/co_citation_input_50_docs/'
centroid_directory = './input/centroidcandidates/'
seqclu_directory = './input/seqclu/'

authors_df = create_authors_table(publications_directory)
print(authors_df)
co_citations_df = create_co_citation_table(co_citations_directory)
print(co_citations_df)
centroid_df = create_centroid_table(centroid_directory)
print(centroid_df)
seqclu_df = create_seqclu_table(seqclu_directory)
print(seqclu_df)

joined_table = pd.merge(centroid_df, seqclu_df, on='Filename', how='inner')
print(joined_table)

# see thesis for more explanations (section "Anwendung auf Autoren- und Co-Zitationsgraphen")

final_table_author = pd.merge(joined_table, authors_df, on='Filename', how='outer')
final_table_co_citation = pd.merge(joined_table, co_citations_df, on='Filename', how='outer')
cleaned_final_table_author = final_table_author.dropna()
cleaned_final_table_co_citation = final_table_co_citation.dropna()

print(cleaned_final_table_co_citation)


def plot_clusters_histogram(author_stats, stats_filename):
    authors_with_multiple_pubs = author_stats[author_stats['Filename'] > 1]
    authors_with_multiple_pubs['ClusterCount'] = authors_with_multiple_pubs['ClusterNumber'].apply(len)

    cluster_count_freq = authors_with_multiple_pubs['ClusterCount'].value_counts().sort_index()

    plt.figure(figsize=(10, 5))
    plt.bar(cluster_count_freq.index, cluster_count_freq.values, color='skyblue', edgecolor='black')
    plt.title('Number of Clusters for Authors with More than One Publication')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Number of Authors')
    plt.xticks(cluster_count_freq.index)  
    plt.grid(False)  # disable  grid
    plt.savefig(f"{stats_filename}_multi_pub_clusters_bar_chart.png")


def create_author_graph_and_analyze_diversity(cleaned_final_table, graph_filename, stats_filename):
    G = nx.Graph()
    for filename, group in cleaned_final_table.groupby('Filename'):
        authors = group['Author'].unique()
        cluster_number = group['ClusterNumber'].iloc[0]
        for i in range(len(authors)):
            for j in range(i+1, len(authors)):
                G.add_node(authors[i])
                G.add_node(authors[j])
                G.add_edge(authors[i], authors[j], cluster=cluster_number)
    color_map = {
        '1': 'red', '2': 'blue', '3': 'green', '4': 'yellow', 
        '5': 'orange', '6': 'purple', '7': 'brown', '8': 'pink', 
        '9': 'gray', '10': 'cyan'
    } # can be adjusted as desired

    edge_colors = [color_map.get(str(G[u][v]['cluster']), 'black') for u, v in G.edges()]
    nx.write_gexf(G, graph_filename)

    author_stats = cleaned_final_table.groupby('Author').agg({'Filename': pd.Series.nunique,
                                                              'ClusterNumber': lambda x: list(x.unique())})

    # count authors with more than 1 publication in the same cluster
    same_cluster_count = author_stats.apply(lambda x: x['Filename'] > 1 and len(x['ClusterNumber']) == 1, axis=1).sum()

    # count authors with more than 1 publication in multiple clusters
    multiple_clusters_count = author_stats.apply(lambda x: x['Filename'] > 1 and len(x['ClusterNumber']) > 1, axis=1).sum()

    total_unique_authors = cleaned_final_table['Author'].nunique()
    most_common_cluster = cleaned_final_table['ClusterNumber'].mode()[0]
    stats_data = {
        'Authors in >1 Pub Same Cluster': same_cluster_count,
        'Authors in >1 Pub Multiple Clusters': multiple_clusters_count,
        'Total Unique Authors': total_unique_authors,
        'Most Common Cluster': most_common_cluster
    }
    stats_df = pd.DataFrame.from_dict(stats_data, orient='index', columns=['Value'])

    # save the statistics to csv
    stats_df.to_csv(stats_filename)

    plot_clusters_histogram(author_stats, 'author_graph_stats')
    return G, stats_df


def create_co_citation_graph(cleaned_final_table, graph_filename, max_rows=None):
    # if max_rows is set, limit the DataFrame to that number of rows. reason was that the resulting graphs were way too large because too many co-citation relations existed within the tested dataset.
    if max_rows is not None:
        cleaned_final_table = cleaned_final_table.head(max_rows)

    G = nx.Graph()
    color_map = {
        '1': 'red', '2': 'blue', '3': 'green', '4': 'yellow', 
        '5': 'orange', '6': 'purple', '7': 'brown', '8': 'pink', 
        '9': 'gray', '10': 'cyan'
    }
    for _, row in tqdm(cleaned_final_table.iterrows(), total=cleaned_final_table.shape[0]):
        G.add_edge(row['Author1'], row['Author2'], cluster=row['ClusterNumber'])
    
    edge_colors = [color_map.get(str(G[u][v]['cluster']), 'black') for u, v in G.edges()]
    nx.write_gexf(G, graph_filename)
    return G


G_author, sorted_authors = create_author_graph_and_analyze_diversity(cleaned_final_table_author, 
                                                                     "co_author_graph_with_topic.gexf", 
                                                                     "author_stats.csv")

G_co_citation = create_co_citation_graph(cleaned_final_table_co_citation,"co_citation_graph_with_topic.gexf")


