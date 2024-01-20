import requests
import xml.etree.ElementTree as ET
import os
import pandas as pd
import shutil
from PyPDF2 import PdfReader
from pathlib import Path


def create_output_folder(output_folder):
    os.makedirs(output_folder, exist_ok=True)


def process_pdf_with_grobid(output_folder, filename):
    try:
        url = 'http://localhost:8070/api/processFulltextDocument'
        file_path = f'./input/docs/{filename}.pdf'
        file = {'input': open(file_path, 'rb')}

        response = requests.post(url, files=file)

        # check if request was successful
        if response.status_code == 200:
            os.makedirs(output_folder, exist_ok=True)
            output_path = os.path.join(output_folder, f'{filename}.xml')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(response.text)

            # check if response is valid XML (not the case if something with grobid went wrong)
            try:
                root = ET.fromstring(response.text)
                return response.text, filename
            except ET.ParseError as parse_error:
                print(
                    f'Error occurred while parsing XML for {filename}: {str(parse_error)}')
                return None, filename

        else:
            print('Error occurred:', response.status_code)
            return None, filename

    except Exception as e:
        print(f'Error occurred while processing {filename}: {str(e)}')
        return None, filename


def extract_author_names(output_folder, xml_data, filename):
    try:
        if xml_data is None:
            print(
                f'Error occurred while processing {filename}. XML data is None.')
            return []

        root = ET.fromstring(xml_data)
        author_elements = root.findall(
            './/{http://www.tei-c.org/ns/1.0}sourceDesc/{http://www.tei-c.org/ns/1.0}biblStruct/{http://www.tei-c.org/ns/1.0}analytic/{http://www.tei-c.org/ns/1.0}author') # hard coded element link 

        authors = []
        for author_element in author_elements:
            forename_element = author_element.find(
                './/{http://www.tei-c.org/ns/1.0}forename')
            surname_element = author_element.find(
                './/{http://www.tei-c.org/ns/1.0}surname')
            if forename_element is not None and surname_element is not None:
                forename = forename_element.text.strip()
                surname = surname_element.text.strip()
                author = f"{forename} {surname}" # direkte verknüpfung
                authors.append(author)

        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, f'{filename}_authors.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            for author in authors:
                f.write(author + '\n')
        # print(f'Author names saved as {output_path}')

        return authors

    except Exception as e:
        print(f'Error occurred while processing {filename}: {str(e)}')
        return []


def extract_full_text(output_folder, xml_data, filename):
    root = ET.fromstring(xml_data)
    text_elements = root.findall(
        './/{http://www.tei-c.org/ns/1.0}body//{http://www.tei-c.org/ns/1.0}p')
    text = ""
    for element in text_elements:
        for child in element.iter():
            if child.tag == '{http://www.tei-c.org/ns/1.0}ref':
                if child.tail is not None:
                    text += child.tail.strip() + " "
            elif child.text:
                text += child.text.strip() + " "
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f'{filename}_full_text.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text.strip())
    #print(f'Full text saved as {output_path}')
    return text.strip()


def create_publication_table(output_folder):
    table_data = []
    for filename in os.listdir(output_folder):
        if filename.endswith('_authors.txt'):
            # remove the "_authors.txt" part of the file names (for easier identification which data  belong to which document)
            publication_name = filename[:-12]
            authors = []
            with open(os.path.join(output_folder, filename), 'r', encoding='utf-8') as f:
                authors = [line.strip() for line in f.readlines()]
            table_data.append((publication_name, authors))
    df = pd.DataFrame(table_data, columns=['Publication', 'Authors'])
    return df


def check_valid_pdf(file_path):
    try:
        with open(file_path, 'rb') as f:
            try:
                pdf = PdfReader(f)
                info = pdf.metadata
                if info:
                    return True
                else:
                    return False
            except Exception as e:
                return False
    except FileNotFoundError:
        return False


def export_valid_pdfs(input_folder, output_folder):
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    all_files = [f for f in os.listdir(input_folder) if f.endswith('.pdf')]
    total_files = len(all_files)

    print(f"Found {total_files} PDF files in {input_folder}")

    valid_files = 0
    for i, filename in enumerate(all_files, start=1):
        file_path = os.path.join(input_folder, filename)
        if check_valid_pdf(file_path):
            shutil.copy(file_path, output_folder)
            valid_files += 1
            print(
                f"File {i} of {total_files} is valid and copied to the output folder")
        else:
            print(f"File {i} of {total_files} is invalid")

    print(
        f"Finished processing. {valid_files} of {total_files} files were valid and copied to {output_folder}")


# helper function for moving
def move_file_if_exists(old_dir: Path, new_dir: Path, filename: str):
    old_path = old_dir / filename
    if old_path.exists():
        shutil.move(old_path, new_dir / filename)
        return True
    return False


# moving functions, checks if there are any authors and if yes moves the whole fileset
def move_publication_files(output_folder):
    print("_______________________________\n")
    output_folder = Path(output_folder)
    publications_folder = output_folder / "publications"

    publications_folder.mkdir(exist_ok=True)

    files_moved = 0
    for file in output_folder.iterdir():
        if file.suffix == '.txt' and file.stem.endswith('_authors'):
            publication_name = file.stem[:-8]  # removing "_authors" again

            try:
                with file.open('r', encoding='utf-8') as f:
                    lines = f.readlines()
                if len(lines) == 0:  # skip if authors file is empty
                    continue
            except UnicodeDecodeError:
                print(f"File {file} could not be read due to encoding issues.")
                continue

            # move the authors file to the "publications" subdirectory
            if move_file_if_exists(output_folder, publications_folder, file.name):
                files_moved += 1

            # move the publication file (same name) to the "publications" subdirectory
            if move_file_if_exists(output_folder, publications_folder, f"{publication_name}.xml"):
                files_moved += 1

            # move the full text (same name) to the "publications" subdirectory
            if move_file_if_exists(output_folder, publications_folder, f"{publication_name}_full_text.txt"):
                files_moved += 1

    print(f"Total files moved: {files_moved}")
