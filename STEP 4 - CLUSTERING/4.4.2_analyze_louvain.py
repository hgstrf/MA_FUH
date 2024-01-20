import shutil
from collections import defaultdict
import random
import matplotlib.pyplot as plt
import os
import ast
import pandas as pd


folder_path = './input/centroidcandidates/'

def read_txt_files(folder_path):
    all_centroids = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            with open(os.path.join(folder_path, file_name), 'r') as file:
                line = file.readline().strip()
                dict_str = line[line.index(
                    "{"): line.index("}") + 1].replace('=', ':')

                if dict_str == '{}':
                    continue

                split_data = dict_str[1:-1].split(',')
                new_data = ', '.join(
                    [f'"{item.split(":")[0].strip()}": {item.split(":")[1].strip()}' for item in split_data])
                dict_str = "{" + new_data + "}"
                data = ast.literal_eval(dict_str)
                first_word = list(data.keys())[0]
                all_centroids.append((first_word, file_name))
    return all_centroids


def analyze_results():
    community_counter = defaultdict(int)
    community_words = defaultdict(list)
    word_to_community = {}

    with open('./output/louvain_results/results.txt', 'r') as file:
        for line in file:
            word, community = line.strip().split(", ")
            community_counter[community] += 1
            community_words[community].append(word)
            word_to_community[word] = community

    print("Community Analysis:")
    for community, count in sorted(community_counter.items(), key=lambda x: x[1]):
        print(f"Community {community} has {count} labels")

    return word_to_community, community_words


def clear_output_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


### for export

def map_file_names(centroid_file):
    return centroid_file.replace('centroid_candidates_sorted_', 'clusters_')

def create_louvain_mapping(word_to_community):
    unique_communities = set(word_to_community.values())
    mapping = {community: i+1 for i, community in enumerate(unique_communities)}
    return mapping

def append_community_to_clusters(trc_output_folder, word_to_community, all_centroids, louvain_mapping):
    for first_word, centroid_file in all_centroids:
        community_number = word_to_community.get(first_word, "Not Found")
        if community_number != "Not Found":
            mapped_community_number = louvain_mapping[community_number]
            cluster_file_name = map_file_names(centroid_file)
            cluster_file_path = os.path.join(trc_output_folder, cluster_file_name)

            if os.path.exists(cluster_file_path):
                with open(cluster_file_path, 'r') as file:
                    lines = file.readlines()

                with open(cluster_file_path, 'w') as file:
                    for index, line in enumerate(lines):
                        original_line = line.strip()
                        print(f"Original line: {original_line}")  
                        if original_line:
                            if index == 0 and not original_line.endswith('louvain'):
                                # add 'louvain' to the header
                                line = f"{original_line},louvain"
                            elif index > 0:
                                line = f"{original_line},{mapped_community_number}"
                            print(f"Updated line: {line}")  
                            file.write(f"{line}\n")



if __name__ == "__main__":
    all_centroids = read_txt_files(folder_path)

    trc_output_folder = './output/louvain_results/TRCs/'
    community_output_folder = './output/louvain_results/Communities/'
    clustering_output_folder = './output/CLUSTERING/'
    os.makedirs(trc_output_folder, exist_ok=True)
    os.makedirs(community_output_folder, exist_ok=True)

    clear_output_folder(trc_output_folder)  
    clear_output_folder(community_output_folder)

    word_to_community, community_words = analyze_results()

    trc_community_counter = defaultdict(int)  
    community_to_trcs = defaultdict(list)  

    for first_word, file_name in all_centroids:
        community_number = word_to_community.get(first_word, "Not Found")
        print(
            f"The centroid {first_word} from file {file_name} belongs to community {community_number}.")

        if community_number != "Not Found":
            trc_community_counter[community_number] += 1 
            community_to_trcs[community_number].append(first_word)

    # export results as txt
    for first_word, community in trc_community_counter.items():
        with open(os.path.join(trc_output_folder, f"{first_word}.txt"), 'w') as file:
            file.write(f"Community: {community}")
    for community, trcs in community_to_trcs.items():
        unique_trcs = set(trcs)  # remove duplicates
        with open(os.path.join(community_output_folder, f"Community_{community}.txt"), 'w') as file:
            for trc in unique_trcs:
                file.write(f"{trc}\n")

    plt.bar(trc_community_counter.keys(), trc_community_counter.values(), color="skyblue")
    plt.xlabel("Community Number")
    plt.ylabel("Number of TRCs")
    plt.title("TRCs per Community")
    plt.show()


    # ################## new visu with cumulative ########################################

    sorted_items = sorted(trc_community_counter.items(), key=lambda x: x[1], reverse=True)
    communities, trc_counts = zip(*sorted_items)
    total_trcs = sum(trc_counts)
    percentages = [(count / total_trcs * 100) for count in trc_counts]
    bars = plt.bar(communities, trc_counts, color="skyblue", edgecolor='black')

    plt.xlabel("Community Number")
    plt.ylabel("Number of TRCs")
    plt.title("TRCs per Community")
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f"{round(yval/total_trcs*100, 1)}%", ha='center', va='bottom')
    ax2 = plt.gca().twinx()
    cumulative_percentage = [sum(trc_counts[:i+1]) / total_trcs * 100 for i in range(len(trc_counts))]
    ax2.plot(communities, cumulative_percentage, color='green', marker='o', linestyle='dashed', linewidth=2, markersize=6)
    ax2.set_ylabel('Cumulative Percentage (%)', color='green')
    ax2.set_ylim(0, 110)
    plt.show()

    louvain_mapping = create_louvain_mapping(word_to_community)
    append_community_to_clusters(clustering_output_folder, word_to_community, all_centroids, louvain_mapping)
    print('done')

