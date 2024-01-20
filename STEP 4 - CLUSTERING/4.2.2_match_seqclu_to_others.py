import os
import re
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

def read_cluster_files(folder_path):
    clusters = {}
    for file_name in os.listdir(folder_path):
        if file_name.startswith('furthest_init_cluster') and file_name.endswith('.txt'):
            cluster_number = int(file_name.split('_')[-1].split('.')[0])
            with open(os.path.join(folder_path, file_name), 'r') as file:
                clusters[cluster_number] = [word.strip() for word in file.readlines()]
    return clusters

def read_centroid_candidates(folder_path):
    all_trcs = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            with open(os.path.join(folder_path, file_name), 'r') as file:
                line = file.readline().strip()
                dict_str = line[line.index("{"): line.index("}") + 1].replace('=', ':')

                if dict_str == '{}':
                    continue

                split_data = dict_str[1:-1].split(',')
                first_noun = None
                for item in split_data:
                    match = re.match(r'\s*(\w+):', item)
                    if match:
                        first_noun = match.group(1)
                        break

                if first_noun is not None:
                    all_trcs[file_name.rstrip('.txt')] = first_noun
    return all_trcs

def match_centroid_to_cluster(centroids, clusters):
    centroid_cluster_mapping = {}
    for file_name, centroid in centroids.items():
        for cluster_number, words in clusters.items():
            if centroid in words:
                centroid_cluster_mapping[file_name] = cluster_number
                break
    return centroid_cluster_mapping


def update_cluster_files(clustering_folder, centroid_cluster_matches):
    for file_name in os.listdir(clustering_folder):
        if file_name.endswith('.txt'):
            transformed_name = 'centroid_candidates_sorted_' + file_name[len('clusters_'):-len('.txt')]

            file_path = os.path.join(clustering_folder, file_name)
            with open(file_path, 'r') as file:
                lines = file.readlines()

            header = lines[0].strip() + ',seqclu\n'
            values = lines[1].strip()
            cluster_number = centroid_cluster_matches.get(transformed_name, 'NA')
            updated_line = f'{values},{cluster_number}\n'

            with open(file_path, 'w') as file:
                file.writelines([header, updated_line])

clusters_path = './output/SeqClu/'
centroid_path = './input/centroidcandidates/'

clusters = read_cluster_files(clusters_path)
centroid_candidates = read_centroid_candidates(centroid_path)

# match centroids to clusters
centroid_cluster_matches = match_centroid_to_cluster(centroid_candidates, clusters)
print(centroid_cluster_matches)

cluster_counts = Counter(centroid_cluster_matches.values())
sorted_cluster_counts = dict(sorted(cluster_counts.items()))

plt.figure(figsize=(10, 5))
sns.barplot(x=list(sorted_cluster_counts.keys()), y=list(sorted_cluster_counts.values()))
plt.title('SeqClu - Number of Documents per Cluster')
plt.xlabel('Cluster Number')
plt.ylabel('Number of Documents')
plt.show()

clustering_folder_path = './output/CLUSTERING/'

update_cluster_files(clustering_folder_path, centroid_cluster_matches)