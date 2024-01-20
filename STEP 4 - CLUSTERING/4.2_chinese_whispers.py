import networkx as nx
import collections
import random
import os
import pickle
import matplotlib.pyplot as plt

def chinese_whispers(graph, iterations=20):
    for node in graph.nodes():
        graph.nodes[node]['label'] = node

    for _ in range(iterations):
        all_nodes = list(graph.nodes())
        random.shuffle(all_nodes)

        for node in all_nodes:
            label_weights = collections.defaultdict(int)

            for neighbor in graph.neighbors(node):
                weight = graph[node][neighbor].get('weight', 1)
                neighbor_label = graph.nodes[neighbor]['label']

                label_weights[neighbor_label] -= weight

            new_label = max(label_weights, key=label_weights.get)
            graph.nodes[node]['label'] = new_label


def find_most_connected_larger_cluster(label, clusters, graph):
    connections = collections.defaultdict(float)

    for node in clusters[label]:
        for neighbor in graph.neighbors(node):
            neighbor_label = graph.nodes[neighbor]['label']
            if neighbor_label != label and len(clusters[neighbor_label]) >= 3:
                connections[neighbor_label] += graph[node][neighbor].get(
                    'weight', 0)

    return max(connections, key=connections.get) if connections else label


def calculate_mean_weights(graph, clusters):
    mean_weights = {}
    all_mean_weights = []

    for cluster_label, nodes in clusters.items():
        cluster_mean_weights = {}
        cluster_mean_sum = 0.0
        node_count = 0

        for node in nodes:
            total_weight = 0.0
            count = 0
            for other_node in nodes:
                if node != other_node:
                    weight = graph[node][other_node].get('weight', 0)
                    total_weight += weight
                    count += 1

            if count > 0:
                mean_weight = total_weight / count
            else:
                mean_weight = 0.0

            cluster_mean_weights[node] = mean_weight
            cluster_mean_sum += mean_weight
            node_count += 1
            all_mean_weights.append(mean_weight)

        cluster_mean = cluster_mean_sum / node_count if node_count > 0 else 0
        cluster_mean_weights['cluster_mean'] = cluster_mean
        mean_weights[cluster_label] = cluster_mean_weights

    global_mean = sum(all_mean_weights) / \
        len(all_mean_weights) if all_mean_weights else 0

    return mean_weights, global_mean


def visualize_clusters_with_weights(clusters, mean_weights):
    fig, ax = plt.subplots()

    y_offset = 0
    for cluster_label, words in clusters.items():
        ax.text(0.1, y_offset,
                f"Cluster {cluster_label} (Mean Weight: {mean_weights[cluster_label]['cluster_mean']:.2f}):", fontsize=12, fontweight='bold')
        words_with_weights = [
            f"{word} ({mean_weights[cluster_label][word]:.2f})" for word in words]
        ax.text(2.0, y_offset, ', '.join(words_with_weights), fontsize=12)
        y_offset -= 1

    ax.axis('off')
    plt.show()


output_directory = './graphs/'
graph_file_name = 'centroid_graph.gpickle'
graph_file_path = os.path.join(output_directory, graph_file_name)

if not os.path.exists(graph_file_path):
    print(f"The graph file {graph_file_path} does not exist.")
else:
    with open(graph_file_path, 'rb') as f:
        loaded_graph = pickle.load(f)

    chinese_whispers(loaded_graph, iterations=100)

    # create initial clusters
    clusters = collections.defaultdict(list)
    for node, data in loaded_graph.nodes(data=True):
        label = data.get('label', None)
        if label is not None:
            clusters[label].append(node)

    # post-process clusters
    merged_clusters = {}
    for label, nodes in clusters.items():
        if len(nodes) < 0:  # merge small clusters, can be removed or changed
            new_label = find_most_connected_larger_cluster(
                label, clusters, loaded_graph)
            merged_clusters.setdefault(new_label, []).extend(nodes)
        else:
            merged_clusters.setdefault(label, []).extend(nodes)

    print("Merged Clusters:", merged_clusters)


    mean_weights, global_mean = calculate_mean_weights(
        loaded_graph, merged_clusters)
    print("Mean Weights:")
    min_mean_weight = float('inf')
    best_cluster_label = None

    for cluster_label, cluster_mean_weights in mean_weights.items():
        print(f"Cluster {cluster_label}:")
        for node, mean_weight in cluster_mean_weights.items():
            if node == 'cluster_mean':
                print(f"  Cluster Mean Weight: {mean_weight}")
            else:
                print(f"  Node {node}: Mean Weight {mean_weight}")

        if cluster_mean_weights['cluster_mean'] < min_mean_weight:
            min_mean_weight = cluster_mean_weights['cluster_mean']
            best_cluster_label = cluster_label

    print(f"Global Mean of All Mean Weights: {global_mean}")
    print(
        f"Best Cluster (Minimum Mean Weight) is Cluster {best_cluster_label} with Mean Weight {min_mean_weight}")
    print(f"Amount of clusters: {len(mean_weights)}")

    color_map = {}
    for color, nodes in enumerate(merged_clusters.values()):
        for node in nodes:
            color_map[node] = color
    node_colors = [color_map[node] for node in loaded_graph.nodes()]

    cluster_graph = nx.Graph()

    for cluster_nodes in merged_clusters.values():
        for i, node1 in enumerate(cluster_nodes):
            for j, node2 in enumerate(cluster_nodes):
                if i < j:  # avoid duplicate edges and self-loops
                    cluster_graph.add_edge(node1, node2)

    cluster_node_colors = [color_map[node] for node in cluster_graph.nodes()]

    # ----------- Visu 1: uncolored---------------
    original_pos = nx.spring_layout(loaded_graph)
    nx.draw(loaded_graph, original_pos, node_color=[node_colors[0]] * len(
        loaded_graph.nodes()), with_labels=False, edge_color='none', alpha=0.5)

    #nx.draw_networkx_edges(cluster_graph, original_pos, edge_color='r')

    plt.title("Clusters in Loaded Graph with Internal Edges")
    plt.show()

    # ----------- Visu 2: colored---------------
   # original_pos = nx.spring_layout(loaded_graph)
    nx.draw(loaded_graph, original_pos, node_color=node_colors,
            with_labels=False, edge_color='none', alpha=0.5)

    #nx.draw_networkx_edges(cluster_graph, original_pos, edge_color='r')

    plt.title("Clusters in Loaded Graph with Internal Edges")
    plt.show()

    # ----------- Visu 3: colored & sorted---------------
    cluster_pos = nx.spring_layout(cluster_graph, k=0.2)

    nx.draw(cluster_graph, cluster_pos, with_labels=False,
            node_color=cluster_node_colors, edge_color='r', alpha=0.5)
    plt.title("Visualizing Cluster Graph with Consistent Node Colors")
    plt.show()
