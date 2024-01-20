from neo4j import GraphDatabase
import os
import warnings
from tqdm import tqdm

warnings.filterwarnings("ignore", category=DeprecationWarning)  # deprecationwarnings can be ignored

def check_graph_exists(tx, graph_name):
    query = "CALL gds.graph.exists($graph_name) YIELD exists"
    return tx.run(query, graph_name=graph_name).single()[0]

def create_graph(tx):
    query = (
        "CALL gds.graph.create('test-cocc-graph','SINGLE_NODE','IS_CONNECTED',"
        "{relationshipProperties:['dice','cost']}) "
        "YIELD graphName, nodeCount, relationshipCount, createMillis;"
    )
    return tx.run(query).single()

def calculate_shortest_distance(tx, word1, word2):
    query = (
        "MATCH (source:SINGLE_NODE{name: '" + word1 +
        "'}), (target:SINGLE_NODE {name: '" + word2 + "'}) "
        "CALL gds.shortestPath.dijkstra.stream('test-cocc-graph',{ "
        "sourceNode: id(source), "
        "targetNode: id(target), "
        "relationshipWeightProperty: 'cost' "
        "}) "
        "YIELD totalCost "
        "RETURN totalCost "
    )
    result = tx.run(query)
    return result.single()[0]

uri = "neo4j://localhost:7687"  #  port can be changed, 7687 worked fine for me
driver = GraphDatabase.driver(uri, auth=("username", "password"))

# create graph if it doesnt exist
with driver.session() as session:
    if not session.read_transaction(check_graph_exists, 'test-cocc-graph'):
        graph_info = session.write_transaction(create_graph)
        print("Graph created.")
    else:
        print("Graph 'test-cocc-graph' already exists.")

# list of directories to process, hardcoded, can be adjusted if new methods are added
directories = ['kmeans', 'lda', 'seqclu', 'louvain']

for directory in directories:
    input_directory = f'./output/CLUSTERS/{directory}/'
    output_directory = f'./output/CLUSTERS/DISTANCES/{directory}/'

    os.makedirs(output_directory, exist_ok=True)

    for cluster_filename in os.listdir(input_directory):
        if cluster_filename.endswith('.txt'):
            cluster_path = os.path.join(input_directory, cluster_filename)
            unique_trcs = set()
            with open(cluster_path, 'r') as file:
                for line in file:
                    trc = line.split(': ')[-1].strip()
                    unique_trcs.add(trc)

            # average distances calculation and storing
            output_file_path = os.path.join(output_directory, cluster_filename)
            with open(output_file_path, 'w') as out_file:
                with driver.session() as session:
                    for word1 in tqdm(unique_trcs, desc=f"Calculating distances for {cluster_filename}", unit="word"):
                        total_distance = 0
                        count = 0
                        for word2 in unique_trcs:
                            if word1 != word2:
                                distance = session.write_transaction(calculate_shortest_distance, word1, word2)
                                total_distance += distance
                                count += 1
                        average_distance = total_distance / count if count > 0 else 0
                        out_file.write(f"{word1}: {average_distance}\n")

driver.close()
