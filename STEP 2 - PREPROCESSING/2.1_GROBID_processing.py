import shutil
from functions_analysis import *
from functions import *
from tqdm import tqdm
import os


input_folder = './input/docs'
output_folder = './output/GrobidOutput/publications'
output_folder_authors = './output/Author_infos'

# all pdf files form input
pdf_files = [filename for filename in os.listdir(
    input_folder) if filename.endswith('.pdf')]

# create output folder if not existing
create_output_folder(output_folder)
create_output_folder(output_folder_authors)

# user interaction (user can choose)
while True:
    choice = input("Choose an option:\n1. Process files with Grobid\n2. Move files with 1 or more authors to 'publications'\n3. Generate and analyze publication tables\n4. Exit\n")
    if choice == '1':
        # fitst check, then process all PDFs
        for filename in tqdm(pdf_files, desc='Processing', unit='document'):
            pdf_path = os.path.join(input_folder, filename)

            if check_valid_pdf(pdf_path):
                try:
                    output = process_pdf_with_grobid(
                        output_folder, filename[:-4])  #filename without file type (*.pdf or *.txt removed)
                    tqdm.write(
                        f"{output[1]} processed. Author names: {len(extract_author_names(output_folder, output[0], output[1]))}, Full text: {len(extract_full_text(output_folder, output[0], output[1]))}")
                except:
                    tqdm.write(
                        f"{output[1]} processed. {output[1]} has a non-allowed XML. Skipping.")
            else:
                tqdm.write(
                    f"{filename} is not a valid PDF. Skipping processing.")

        print("All documents processed.")
    elif choice == '2':
        # move files with 1 or more authors to another folder 
        move_publication_files(output_folder)
        print("Files with 1 or more authors moved to 'publications'.")
        print("_______________________________")
    elif choice == '3':
        # create publication table
        publication_table = create_publication_table(output_folder)
        result_table = count_publications_per_author(
            publication_table, output_folder_authors)
        print("\Author results Table:")
        print(result_table)

        # statistics
        max_publication_count = result_table['Publication Count'].max()
        average_publication_count = result_table['Publication Count'].mean()
        print("Maximum Publication Count:", max_publication_count)
        print("Average Publication Count:", average_publication_count)

        # show co-author-graph
        visualize_coauthor_graph(result_table,'./output/authorgraph.gexf')

    elif choice == '4':
        print("Exiting the program.")
        break
    else:
        print("_______________________________\n")
        print("Invalid choice. Please try again.")
        print("_______________________________")
