import matplotlib.pyplot as plt

cluster_counter = {}
with open('./output/label_propagation/results.txt', 'r') as file:
    for line in file:
        _, cluster_number = line.strip().split(', ')
        cluster_number = int(cluster_number)

        if cluster_number in cluster_counter:
            cluster_counter[cluster_number] += 1
        else:
            cluster_counter[cluster_number] = 1

total_terms = sum(cluster_counter.values())
most_terms_community = max(cluster_counter.items(), key=lambda x: x[1])

# no of terms with >=3 elements (exclude largest)
sum_3_or_more_excl_largest = sum(count for cluster, count in cluster_counter.items() if count >= 3 and cluster != most_terms_community[0])

# no of terms with 2 elements
sum_exactly_2 = sum(count for count in cluster_counter.values() if count == 2)

# no of terms with 1 element
sum_exactly_1 = sum(count for count in cluster_counter.values() if count == 1)

data = {
    "Largest Community": most_terms_community[1],
    "Comm. with 3+ Terms (excl. largest)": sum_3_or_more_excl_largest,
    "Comm. with 2 Terms": sum_exactly_2,
    "Comm. with 1 Term": sum_exactly_1
}

sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
x_labels, terms_counts = zip(*sorted_data)

bars = plt.bar(x_labels, terms_counts, color="skyblue", edgecolor='black')
plt.xlabel("Community Categories")
plt.ylabel("Number of Terms")
plt.title("Terms per Community")

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, f"{round(yval/total_terms*100, 1)}%", ha='center', va='bottom')
ax2 = plt.gca().twinx()
cumulative_percentage = [sum(terms_counts[:i+1]) / total_terms * 100 for i in range(len(terms_counts))]
ax2.plot(x_labels, cumulative_percentage, color='green', marker='o', linestyle='dashed', linewidth=2, markersize=6)
ax2.set_ylabel('Cumulative Percentage (%)', color='green')
ax2.set_ylim(0, 110)
plt.show()
