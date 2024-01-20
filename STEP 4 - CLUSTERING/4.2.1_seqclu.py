import networkx as nx
import os
import matplotlib.pyplot as plt
import pickle
import itertools
import numpy as np
from heapq import nlargest
import random


def mean_weight(graph, cluster):
    weights = []
    if len(cluster) <= 1:
        return np.nan
    for pair in itertools.combinations(cluster, 2):
        weights.append(graph[pair[0]][pair[1]]['weight'])
    return np.mean(weights)


def initialize_clusters_furthest(graph, cluster_count):
    node_distances = {}
    for node in graph.nodes():
        node_distances[node] = sum(
            [graph[node][neighbor]['weight'] for neighbor in graph[node]])

    farthest_nodes = nlargest(
        cluster_count, node_distances, key=node_distances.get)
    clusters = [[node] for node in farthest_nodes]
    return clusters, set(farthest_nodes)


def initialize_clusters(graph, cluster_count):
    nodes = list(graph.nodes())
    random.shuffle(nodes)
    selected_nodes = nodes[:cluster_count]
    clusters = [[node] for node in selected_nodes]
    return clusters, set(selected_nodes)


def custom_clustering(graph, cluster_count, initializer=initialize_clusters, fully_random=False):
    clusters, used_nodes = initializer(graph, cluster_count)
    remaining_nodes = set(graph.nodes()) - used_nodes
    global_means = []

    for node in remaining_nodes:
        print(f"Considering node: {node}")

        if fully_random:
            random_idx = random.randint(0, cluster_count - 1)
            clusters[random_idx].append(node)
            print(
                f"  - Fully Random: Node {node} added to Cluster {random_idx + 1}")
        else:
            best_cluster_idx = None
            best_mean_weight = float('inf')

            for idx, cluster in enumerate(clusters):
                cluster.append(node)
                cur_mean_weight = mean_weight(graph, cluster)

                print(
                    f"  - Adding to Cluster {idx + 1} gives mean weight: {cur_mean_weight}")

                if cur_mean_weight < best_mean_weight:
                    best_mean_weight = cur_mean_weight
                    best_cluster_idx = idx

                cluster.remove(node)

            clusters[best_cluster_idx].append(node)
            print(f"  - Node {node} added to Cluster {best_cluster_idx + 1}")

        all_mean_weights = [mean_weight(graph, cluster)
                            for cluster in clusters]
        global_mean = np.nanmean(
            [mw for mw in all_mean_weights if not np.isnan(mw)])
        global_means.append(global_mean)
        print(f"  - Global mean weight: {global_mean}")
        print(len(clusters[0]))

    return clusters, global_means

def export_clusters(clusters, output_directory, file_name_prefix):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for idx, cluster in enumerate(clusters):
        file_path = os.path.join(output_directory, f'{file_name_prefix}_cluster_{idx + 1}.txt')
        with open(file_path, 'w') as f:
            for node in cluster:
                f.write(f'{node}\n')
    print(f"Exported clusters to directory: {output_directory}")


output_directory = './graphs/'
graph_file_name = 'centroid_graph.gpickle'
graph_file_path = os.path.join(output_directory, graph_file_name)

if not os.path.exists(graph_file_path):
    print(f"The graph file {graph_file_path} does not exist.")
else:
    with open(graph_file_path, 'rb') as f:
        loaded_graph = pickle.load(f)

    cluster_center_no = 10

    clusters_fully_random, global_fully_random = custom_clustering(
        loaded_graph, cluster_center_no, fully_random=True)
    clusters_random, global_means_random = custom_clustering(
        loaded_graph, cluster_center_no, initializer=initialize_clusters)
    clusters_furthest, global_means_furthest = custom_clustering(
        loaded_graph, cluster_center_no, initializer=initialize_clusters_furthest)

    plt.plot(global_means_random, label='1: Randomly initialized Clusters')
    plt.plot(global_means_furthest,
             label='2: Clusters initialized by furthest distance')
    plt.plot(global_fully_random, label='3: Full Random Clustering')
    plt.xlabel('Iterations')
    plt.ylabel('Global Mean Weight')
    plt.legend(loc='best')
    plt.title('Change in Global Mean Weight')
    plt.show()

    output_directory2 = './output/SeqClu/'
    export_clusters(clusters_furthest, output_directory2, 'furthest_init')
