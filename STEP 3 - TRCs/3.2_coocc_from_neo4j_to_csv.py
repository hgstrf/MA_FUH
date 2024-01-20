from neo4j import GraphDatabase
import csv

uri = "bolt://localhost:7687"  # adjust ports if different on other systems (7687 worked fine for me)
driver = GraphDatabase.driver(uri, auth=("username", "password"))  # login

def export_to_csv(query, file_name):
    with driver.session() as session:
        result = session.run(query)
        with open(file_name, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(result.keys())  
            for record in result:
                writer.writerow(record.values())

export_to_csv(
    "MATCH (n) RETURN id(n) as id, labels(n) as labels, n.name as name",
    "nodes.csv"
)
export_to_csv(
    "MATCH ()-[r]->() RETURN id(r) as id, type(r) as type, startNode(r).name as source, endNode(r).name as target",
    "relationships.csv"
)
driver.close()
