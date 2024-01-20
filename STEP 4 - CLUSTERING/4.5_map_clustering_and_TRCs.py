import os
import re
import csv

def extract_first_centroid_candidate(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        match = re.search(r'\{(.*?)=', content)
        if match:
            return match.group(1)
    return None

def process_centroid_files(folder_path):
    mapping = {}
    for file in os.listdir(folder_path):
        if file.startswith("centroid_candidates_sorted_") and file.endswith(".txt"):
            file_path = os.path.join(folder_path, file)
            centroid_candidate = extract_first_centroid_candidate(file_path)
            if centroid_candidate:
                filename = file[len("centroid_candidates_sorted_"):-4]
                mapping[filename] = centroid_candidate
    return mapping

def process_cluster_files(folder_path, centroid_mapping):
    cluster_mapping = {'kmeans': {}, 'lda': {}, 'seqclu': {}, 'louvain': {}}
    for file in os.listdir(folder_path):
        if file.startswith("clusters_") and file.endswith(".txt"):
            with open(os.path.join(folder_path, file), 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                headers = [header.lower() for header in next(csvreader)]  # headers to lower case

                for method in cluster_mapping:
                    if method in headers:  # check if method exists in the headers (such as LDA or smth)
                        method_index = headers.index(method)
                        for row in csvreader:
                            cluster = row[method_index]
                            filename = file[len("clusters_"):-4]
                            if cluster not in cluster_mapping[method]:
                                cluster_mapping[method][cluster] = []
                            if filename in centroid_mapping:
                                cluster_mapping[method][cluster].append((filename, centroid_mapping[filename]))
                        csvfile.seek(0)
                        next(csvreader)  # skip header row on subsequent reads
                    else:
                        print(f"Warning: Method '{method}' not found in file '{file}'")

    return cluster_mapping


def write_clusters_to_files(cluster_mapping, base_folder):
    for method, clusters in cluster_mapping.items():
        method_folder = os.path.join(base_folder, method)
        os.makedirs(method_folder, exist_ok=True)
        for cluster, files in clusters.items():
            with open(os.path.join(method_folder, f"{cluster}.txt"), 'w') as file:
                for filename, centroid in files:
                    file.write(f"{filename}: {centroid}\n")

centroid_folder_path = './input/centroidcandidates'
centroid_mapping = process_centroid_files(centroid_folder_path)

cluster_folder_path = './output/CLUSTERING'
cluster_mappings = process_cluster_files(cluster_folder_path, centroid_mapping)

output_folder = './output/CLUSTERS'
write_clusters_to_files(cluster_mappings, output_folder)
