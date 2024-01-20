import random  
import matplotlib.pyplot as plt  
from collections import defaultdict
from neo4j import GraphDatabase
from itertools import combinations
import networkx as nx
import os
import ast
from datetime import datetime
from tqdm import tqdm

uri = "bolt://localhost:7687"  # port can be changed if needed, 7687 worked fine for me
driver = GraphDatabase.driver(uri, auth=("username", "password"))

G = nx.Graph()

folder_path = './input/centroidcandidates/'
output_directory = './output/centroid_graph_info/'

if not os.path.exists(output_directory):
    os.makedirs(output_directory)


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


def run_query(driver):
    output_path = './output/06_louvain_results/'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    with driver.session() as session, open(f"{output_path}results.txt", "w") as output_file:
        query = """
        CALL gds.louvain.stream('test-cocc-graph', {relationshipWeightProperty: 'cost'})
        YIELD nodeId, communityId as Community
        RETURN gds.util.asNode(nodeId).name as Name, Community
        ORDER BY Community, Name
        """
        result = session.run(query)
        for record in result:
            line = f"{record['Name']}, {record['Community']}\n"
            output_file.write(line)


def analyze_results():
    community_counter = defaultdict(int)
    community_words = defaultdict(list)  #

    with open('./output/06_louvain_results/results.txt', 'r') as file:
        for line in file:
            word, community = line.strip().split(", ")
            community_counter[community] += 1
            community_words[community].append(word)

    exemplary_words = {community: random.choice(
        words) for community, words in community_words.items()}

    sorted_communities = sorted(community_counter.items(), key=lambda x: x[1])

    print("Community Analysis:")
    for community, count in sorted_communities:
        print(f"Community {community} has {count} labels")

    # visualization for communities with more than 3 labels
    filtered_communities = [(c, n) for c, n in sorted_communities if n > 3]

    if filtered_communities:
        communities, counts = zip(*filtered_communities)
        exemplary_labels = [f"{c} ({exemplary_words[c]})" for c in communities]
        plt.barh(exemplary_labels, counts, color='skyblue')
        plt.xscale('log')  # x-axis as log scale
        plt.xlabel('Number of Labels (log scale)')
        plt.ylabel('Community (Random Exemplary Word)')
        plt.title('Number of Labels per Community (More than 3 labels)')
        plt.show()
    else:
        print("No communities have more than 3 labels.")


def main():
    while True:
        user_input = input(
            "Would you like to run the query again or just analyze the results? (run/analyze/quit): ")

        if user_input.lower() == 'run':
            run_query(driver)

        elif user_input.lower() == 'analyze':
            analyze_results()

        elif user_input.lower() == 'quit':
            print("Exiting program.")
            break

        else:
            print("Invalid option. Please enter 'run', 'analyze', or 'quit'.")


if __name__ == "__main__":
    main()
