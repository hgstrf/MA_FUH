import os
import re
from fuzzywuzzy import fuzz
from collections import Counter
import matplotlib.pyplot as plt


def extract_first_word(input_text):
    match = re.search(r'{([^}]*)', input_text)
    if match:
        data = match.group(1)
        words = data.split(',')
        if words:
            first_word = words[0].split('=')[0].strip()
            return first_word
    return None


def find_similar_words(word_list, threshold=80):
    similar_words = []
    for i in range(len(word_list)):
        for j in range(i + 1, len(word_list)):
            similarity_ratio = fuzz.ratio(word_list[i], word_list[j])
            if similarity_ratio >= threshold:
                similar_words.append((word_list[i], word_list[j]))
    return similar_words


folder_path = 'input/centroidcandidates'
extracted_words = []

for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r') as file:
            contents = file.read()
            first_word = extract_first_word(contents)
            if first_word:
                extracted_words.append(first_word)

unique_words = list(set(extracted_words))
total_unique_words = len(unique_words)
print("Total number of unique words:", total_unique_words)

word_count = Counter(extracted_words)
sorted_word_count = sorted(
    word_count.items(), key=lambda x: x[1], reverse=True)

total_occurrences = sum(word_count.values())

print("{:<15} {:<10} {:<10}".format("Word", "Occurrences", "Percentage"))
print("="*35)

words_occuring_3_or_less = sum(
    1 for count in sorted_word_count if count[1] <= 3)

for word, count in sorted_word_count:
    percentage = (count / total_occurrences) * 100
    print("{:<15} {:<10} {:<10.2f}%".format(word, count, percentage))

print("Number of words occurring 3 times or less:", words_occuring_3_or_less)
print("Out of total unique words:", total_unique_words)


similar_words = find_similar_words(unique_words, threshold=80)

print("Similar Words:")
for word1, word2 in similar_words:
    print(f"{word1} - {word2}")


plt.figure(figsize=(10, 6))
counts = [count for _, count in sorted_word_count[:25]]
words = [word for word, _ in sorted_word_count[:25]]  # get the first 25 words
plt.bar(words, counts, color='blue')
plt.xlabel('Word')
plt.ylabel('Occurrences')
plt.title('Histogram of Word Occurrences (First 25)')
plt.xticks(rotation='vertical')

plt.tight_layout()
plt.show()


plt.figure(figsize=(10, 6))

counts = [count for _, count in sorted_word_count[:25]]
words = [word for word, _ in sorted_word_count[:25]]  

plt.bar(words, counts, color='skyblue', edgecolor='black')
plt.xlabel('Word')
plt.ylabel('Occurrences')
plt.title('Histogram of Word Occurrences (First 25)')
plt.xticks(rotation='vertical')
plt.tight_layout()
plt.show()
