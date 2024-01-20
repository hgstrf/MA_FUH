import os
import ast
import gensim
from gensim import corpora
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


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
                split_data = split_data[:25]

                new_data = ', '.join(
                    [f'"{item.split(":")[0].strip()}": {item.split(":")[1].strip()}' for item in split_data])
                dict_str = "{" + new_data + "}"
                data = ast.literal_eval(dict_str)
                all_docs.append(data)
    return all_docs


def main():
    folder_path = './input/centroidcandidates/'
    all_docs = read_txt_files(folder_path)
    print(all_docs)

    # preprocessing
    documents = [' '.join(list(doc.keys())) for doc in all_docs]
    texts = [[word for word in document.lower().split()]
             for document in documents]
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    lda_model = gensim.models.LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=10,
        random_state=42,
        passes=25,
        alpha='auto',
        eta='auto',
        per_word_topics=False
    )

    # print and save topics to .txt 
    output_directory = './output/LDA/'
    ensure_directory_exists(output_directory)

    for idx, topic in lda_model.print_topics(-1):
        print(f"Topic: {idx} \nWords: {topic}\n")

        with open(os.path.join(output_directory, f'topic_{idx}.txt'), 'w') as topic_file:
            topic_file.write(topic)

    # visu as HTML file
    vis = pyLDAvis.gensim_models.prepare(lda_model, corpus, dictionary)
    pyLDAvis.save_html(vis, 'lda_visualization.html')

    dominant_topics = dominant_topic_for_each_document(lda_model, corpus)


    # update existing files with LDA results
    output_folder = './output/CLUSTERING/'
    for i, file_name in enumerate(os.listdir(output_folder)):
        if file_name.endswith('.txt'):
            output_path = os.path.join(output_folder, file_name)

            with open(output_path, 'r') as file:
                lines = file.readlines()
            if 'lda' not in lines[0]:
                if lines:
                    kmeans_result = lines[1].strip()
                    updated_content = lines[0].strip() + ',lda\n' + kmeans_result + ',' + str(dominant_topics[i]) + '\n'

                    with open(output_path, 'w') as file:
                        file.write(updated_content)

    topic_counts = Counter(dominant_topics)
    sorted_topic_counts = dict(sorted(topic_counts.items(), key=lambda item: item[1], reverse=True))

    # plotting
    plt.figure(figsize=(10, 5))
    sns.barplot(x=list(sorted_topic_counts.keys()), y=list(sorted_topic_counts.values()))
    plt.title('LDA: Number of Documents per Topic')
    plt.xlabel('Topic Number')
    plt.ylabel('Number of Documents')
    plt.show()                    

def dominant_topic_for_each_document(lda_model, corpus):
    dominant_topics = []
    for row in lda_model[corpus]:
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        dominant_topic_num = row[0][0]  # dominant topic number
        dominant_topics.append(dominant_topic_num)
    return dominant_topics


if __name__ == '__main__':
    main()
