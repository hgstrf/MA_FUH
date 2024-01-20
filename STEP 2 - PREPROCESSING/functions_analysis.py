from matplotlib.colors import Normalize
import matplotlib.cm as cm
import os
import re
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def count_publications_per_author(publication_table, output_directory):
    author_counts = {}

    for index, row in publication_table.iterrows():
        publication = row['Publication']
        authors = row['Authors']

        for author in authors:
            if author in author_counts:
                author_counts[author]['Publication Count'] += 1
            else:
                author_counts[author] = {
                    'Publication Count': 1, 'Publications': [], 'Co-Authors': {}}

            author_counts[author]['Publications'].append(publication)

            co_authors = [
                co_author for co_author in authors if co_author != author]

            for co_author in co_authors:
                if co_author in author_counts[author]['Co-Authors']:
                    author_counts[author]['Co-Authors'][co_author] += 1
                else:
                    author_counts[author]['Co-Authors'][co_author] = 1

    # convert author_counts dictionary into table (for easier processing)
    author_counts_table = pd.DataFrame.from_dict(author_counts, orient='index')
    author_counts_table.index.name = 'Author'
    author_counts_table.reset_index(inplace=True)

    os.makedirs(output_directory, exist_ok=True)

    # export data (per author)
    for index, row in author_counts_table.iterrows():
        author_name = row['Author']
        sanitized_author_name = sanitize_filename(author_name)
        file_path = os.path.join(
            output_directory, f'{sanitized_author_name}.txt')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f'Author: {author_name}\n')
            f.write(f'Publication Count: {row["Publication Count"]}\n')
            f.write('Publications:\n')
            for publication in row['Publications']:
                f.write(f'- {publication}\n')
            f.write('Co-Authors:\n')
            for co_author, co_author_count in row['Co-Authors'].items():
                f.write(f'- {co_author} (Co-authorships: {co_author_count})\n')

    return author_counts_table[['Author', 'Publication Count', 'Publications', 'Co-Authors']]


def visualize_coauthor_graph(result_table,export_path):
    G = nx.Graph()

    for index, row in result_table.iterrows():
        author = row['Author']
        publication_count = row['Publication Count']
        G.add_node(author, publications=publication_count)

    for index, row in result_table.iterrows():
        author = row['Author']
        co_authors = row['Co-Authors']
        for co_author in co_authors:
            G.add_edge(author, co_author)

    # set node size based on publication count
    node_size = [d['publications'] * 100 for _, d in G.nodes(data=True)]

    publication_count_values = result_table['Publication Count'].values
    colormap = cm.get_cmap('cool')
    norm = Normalize(vmin=min(publication_count_values),
                     vmax=max(publication_count_values))
    node_color = [colormap(norm(d['publications']))
                  for _, d in G.nodes(data=True)]

    pos = nx.spring_layout(G, seed=42)  # for reproducibility, standard value (42 :D)
    plt.figure(figsize=(12, 8))
    nx.draw_networkx(
        G, pos, with_labels=True, node_size=node_size, node_color=node_color,
        cmap='cool', font_size=10, alpha=0.8, edge_color='gray', width=0.5)
    sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, label='Publication Count')
    plt.title('Co-Author Graph')
    plt.show()
    nx.write_gexf(G, export_path)  # export to file (for later use)