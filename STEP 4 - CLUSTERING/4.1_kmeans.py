import os
import ast
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


def read_txt_files(folder_path):
    all_docs = []

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

                all_docs.append(data)

    return all_docs


folder_path = './input/centroidcandidates/'
all_docs = read_txt_files(folder_path)

documents = [' '.join(list(doc.keys())) for doc in all_docs]
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(documents)

wcss = []
max_clusters = 10  # k, can be changed to whatever
for i in range(1, max_clusters+1):
    kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
    kmeans.fit(X)
    wcss.append(kmeans.inertia_)

plt.figure(figsize=(10, 5))
plt.plot(range(1, max_clusters+1), wcss, marker='o', linestyle='--')
plt.title('Elbow Method')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.show()

optimal_clusters = int(
    input("Enter the optimal number of clusters from the plot: "))

kmeans = KMeans(n_clusters=optimal_clusters, init='k-means++', random_state=42)
labels = kmeans.fit_predict(X)

print("\nTop keywords for each cluster:")
order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
terms = vectorizer.get_feature_names_out()

for i in range(optimal_clusters):
    print(f"\nCluster {i}:")
    for ind in order_centroids[i, :10]:
        print(f"- {terms[ind]}")

# visu: no of docs per cluster
cluster_counts = Counter(labels)
sorted_cluster_counts = dict(sorted(cluster_counts.items(), key=lambda item: item[1], reverse=True))

plt.figure(figsize=(10, 5))
sns.barplot(x=list(sorted_cluster_counts.keys()), y=list(sorted_cluster_counts.values()))
plt.title('k-Means: Number of Documents per Cluster')
plt.show()

print(list(sorted_cluster_counts.keys()))
print(list(sorted_cluster_counts.values()))


# visu: keyword distribution
all_keywords = [keyword for doc in all_docs for keyword in doc.keys()]
keyword_counts = Counter(all_keywords)

plt.figure(figsize=(15, 6))
sns.barplot(x=list(keyword_counts.keys()), y=list(keyword_counts.values()))
plt.xticks(rotation=90)
plt.title('Keyword Distribution')
plt.show()

# visu: weights
plt.figure(figsize=(15, 6))
for keyword in set(all_keywords):
    weights = [doc[keyword] for doc in all_docs if keyword in doc]
    sns.boxplot(y=weights, x=[keyword]*len(weights))
plt.xticks(rotation=90)
plt.title('Weight Distribution for Keywords')
plt.show()


output_folder = './output/CLUSTERING/'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for i, file_name in enumerate(os.listdir(folder_path)):
    if file_name.endswith('.txt'):
        modified_file_name = file_name.replace('centroid_candidates_sorted_', 'clusters_')
        predicted_cluster = kmeans.predict(vectorizer.transform([documents[i]]))[0] # prediction
        output_path = os.path.join(output_folder, modified_file_name)

        with open(output_path, 'w') as output_file:
            output_file.write('kmeans\n')
            output_file.write(str(predicted_cluster))