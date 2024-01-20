import os
import matplotlib.pyplot as plt
import numpy as np

co_author_count = []
max_co_authors = 0
file_with_max_co_authors = ''

# loop through every file in crawler_output directory
for filename in os.listdir('./output_API/txt/'):
    if filename.endswith('.txt'):
        with open(os.path.join('./output_API/txt/', filename), 'r', encoding='utf-8') as f:
            lines = f.readlines()

            co_auth_count = 0
            in_co_author_section = False

            for line in lines:
                line = line.strip()
                if line == "Co-Authors:":
                    in_co_author_section = True
                    continue
                elif line == "Publication ID:":
                    in_co_author_section = False

                if in_co_author_section and line:
                    co_auth_count += 1

            co_author_count.append(co_auth_count)

            if co_auth_count > max_co_authors:
                max_co_authors = co_auth_count
                file_with_max_co_authors = filename

# statistics
min_co_authors = min(co_author_count)
mean_co_authors = np.mean(co_author_count)
median_co_authors = np.median(co_author_count)
print(f"Min Co-Authors: {min_co_authors}, Max Co-Authors: {max_co_authors}, Mean Co-Authors: {mean_co_authors}, Median Co-Authors: {median_co_authors}")
print(f"File with most Co-Authors: {file_with_max_co_authors}")


# draw histograms
plt.figure(figsize=(12, 6))
n, bins, patches = plt.hist(co_author_count, bins=range(
    min_co_authors, max_co_authors + 1), density=True, alpha=0.75)
plt.axvline(mean_co_authors, color='red', linestyle='dashed',
            linewidth=1, label=f'Mean: {mean_co_authors:.2f}')
plt.axvline(median_co_authors, color='green', linestyle='dashed',
            linewidth=1, label=f'Median: {median_co_authors}')
plt.title("Co-Author Counts")
plt.xlabel("Number of Co-Authors")
plt.ylabel("Frequency (%)")
plt.legend()
plt.gca().set_yticklabels(['{:.0f}%'.format(x*100)
                           for x in plt.gca().get_yticks()])
plt.tight_layout()
plt.show()

# new style
plt.hist(co_author_count, bins=20, color='skyblue', edgecolor='black')
plt.xlabel("Number of Co-Authors")
plt.ylabel("Frequency [%]")
plt.title("Co-Author Counts")

plt.axvline(mean_co_authors, color='red', linestyle='dashed', linewidth=1, label=f'Mean: {mean_co_authors:.2f}')
plt.axvline(median_co_authors, color='green', linestyle='dashed', linewidth=1, label=f'Median: {median_co_authors}')

plt.legend()
plt.show()

