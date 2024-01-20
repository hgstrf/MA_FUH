import os
import numpy as np
import matplotlib.pyplot as plt

def calculate_average_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        values = [float(line.split(': ')[1].strip()) for line in lines if float(line.split(': ')[1].strip()) != 0]
        count = len(values)
        average = sum(values) / count if count > 0 else 0
    return average, count

def process_folder(folder_path, output_file):
    file_averages = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            average, count = calculate_average_from_file(file_path)
            if count > 0:  # Only consider files with non-zero values
                file_averages.append(f"{filename},{average},{count}\n")

    with open(output_file, 'w') as file:
        file.writelines(file_averages)

def read_means_and_counts(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        means = []
        counts = []
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) == 3 and float(parts[1]) != 0:
                means.append(float(parts[1]))
                counts.append(int(parts[2]))
    return means, counts

base_path = './output/CLUSTERS/DISTANCES/'
subfolders = ['kmeans', 'lda', 'louvain', 'seqclu']

for folder in subfolders:
    folder_path = os.path.join(base_path, folder)
    output_file = os.path.join(base_path, f'{folder}_mean.txt')
    process_folder(folder_path, output_file)

fig, ax = plt.subplots()
data_to_plot = []
means_list = [] 

for folder in subfolders:
    mean_file = os.path.join(base_path, f'{folder}_mean.txt')
    means, counts = read_means_and_counts(mean_file)
    if means:  # only add to plot if there are non-zero means
        weighted_means = [mean * count for mean, count in zip(means, counts)]
        data_to_plot.append(weighted_means)
        means_list.append(np.mean(weighted_means))

if data_to_plot: 
    bp = ax.boxplot(data_to_plot, labels=subfolders, patch_artist=True)
    for box in bp['boxes']:
        box.set_facecolor('skyblue')

    for median_line in bp['medians']:
        median_line.set_visible(False)

    for i, mean in enumerate(means_list, start=1):
        ax.hlines(mean, i - 0.25, i + 0.25, color='red', linestyles='solid')

    ax.set_title('Box Plots of Weighted Mean Values')
    plt.show()
else:
    print("No non-zero mean values to display.")


avg_count_list = []
std_dev_count_list = []
avg_distance_list = []
std_dev_distance_list = []
combined_scores = []  

for folder in subfolders:
    mean_file = os.path.join(base_path, f'{folder}_mean.txt')
    distances, counts = read_means_and_counts(mean_file)
    if distances:
        avg_count = np.mean(counts)
        std_dev_count = np.std(counts)
        avg_distance = np.mean(distances)
        std_dev_distance = np.std(distances)

        avg_count_list.append(avg_count)
        std_dev_count_list.append(std_dev_count)
        avg_distance_list.append(avg_distance)
        std_dev_distance_list.append(std_dev_distance)

        combined_scores_1 = []
        combined_scores_2 = []

        for avg_count, std_dev_count, avg_distance, std_dev_distance in zip(avg_count_list, std_dev_count_list, avg_distance_list, std_dev_distance_list):
            combined_score_1 = (avg_count + std_dev_count) * (avg_distance + std_dev_distance)
            combined_score_2 = (avg_count * std_dev_count) * (avg_distance * std_dev_distance)
            # see chapter "Qualitätsanalyse" in thesis for explanations

            combined_scores_1.append(combined_score_1)
            combined_scores_2.append(combined_score_2)
            
    else:
        # Append 0 for each metric if no data
        avg_count_list.append(0)
        std_dev_count_list.append(0)
        avg_distance_list.append(0)
        std_dev_distance_list.append(0)
        combined_scores_1.append(0)
        combined_scores_2.append(0)

# normalize combined scores
max_score_1 = max(combined_scores_1)
max_score_2 = max(combined_scores_2)

normalized_scores_1 = [score / max_score_1 for score in combined_scores_1]
normalized_scores_2 = [score / max_score_2 for score in combined_scores_2]

import numpy as np

def plot_combined_scores(scores1, scores2, title):
    fig, ax = plt.subplots()

    bar_width = 0.35
    index = np.arange(len(subfolders))
    bars1 = ax.bar(index, scores1, bar_width, label='$G_{2}$', color='skyblue', edgecolor='black')
    bars2 = ax.bar(index + bar_width, scores2, bar_width, label='$G_{3}$', color='lightgreen', edgecolor='black')

    def annotate_bars(bars):
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2),
                    verticalalignment='bottom', ha='center', fontsize=8)

    annotate_bars(bars1)
    annotate_bars(bars2)

    ax.set_xlabel('Method')
    ax.set_ylabel('Scores')
    ax.set_title(title)
    ax.set_xticks(index + bar_width / 2)
    ax.set_xticklabels(subfolders)
    ax.legend()

    plt.show()

plot_combined_scores(normalized_scores_1, normalized_scores_2, 'Normalized Comparison')
