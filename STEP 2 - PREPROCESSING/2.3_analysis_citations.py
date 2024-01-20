import os
import xml.etree.ElementTree as ET
import re

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '', name)

def is_valid_name(name):
    pattern = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚàèìòùÀÈÌÒÙäëïöüÄËÏÖÜâêîôûÂÊÎÔÛçñßÇÑ \-\'\.]+$') # allows special characters like "Umlaute" or accents
    return bool(pattern.match(name))


def process_xml_files(output_folder, input_folder):
    try:
        if not os.path.exists(input_folder) or not os.path.isdir(input_folder):
            print(f'Error: Input folder "{input_folder}" does not exist.')
            return

        for filename in os.listdir(input_folder):
            if filename.endswith(".xml"):
                file_path = os.path.join(input_folder, filename)

                tree = ET.parse(file_path)
                root = tree.getroot()
                authors = extract_author_names(root)
                cited_authors = extract_citation_authors(root)

                # write everything to files
                for author in authors:
                    if is_valid_name(author):
                        sanitized_author = sanitize_filename(author)
                        output_path = os.path.join(output_folder, f'{sanitized_author}.txt')
                        with open(output_path, 'a', encoding='utf-8') as f:
                            for cited_author in cited_authors:
                                f.write(cited_author + '\n')

    except Exception as e:
        print(f'Error occurred while processing files in "{input_folder}": {str(e)}')


def extract_author_names(root):
    authors = []
    author_elements = root.findall(
        './/{http://www.tei-c.org/ns/1.0}sourceDesc/{http://www.tei-c.org/ns/1.0}biblStruct/{http://www.tei-c.org/ns/1.0}analytic/{http://www.tei-c.org/ns/1.0}author')
    for author_element in author_elements:
        forename_element = author_element.find('.//{http://www.tei-c.org/ns/1.0}forename')
        surname_element = author_element.find('.//{http://www.tei-c.org/ns/1.0}surname')
        if forename_element is not None and surname_element is not None:
            forename = forename_element.text.strip()
            surname = surname_element.text.strip()
            authors.append(f"{forename} {surname}")
    return authors

def extract_citation_authors(root):
    cited_authors = []
    citation_elements = root.findall(
        './/{http://www.tei-c.org/ns/1.0}text/{http://www.tei-c.org/ns/1.0}back/{http://www.tei-c.org/ns/1.0}div/{http://www.tei-c.org/ns/1.0}listBibl/{http://www.tei-c.org/ns/1.0}biblStruct/{http://www.tei-c.org/ns/1.0}analytic/{http://www.tei-c.org/ns/1.0}author')
    for citation_element in citation_elements:
        forename_element = citation_element.find('.//{http://www.tei-c.org/ns/1.0}forename')
        surname_element = citation_element.find('.//{http://www.tei-c.org/ns/1.0}surname')
        if forename_element is not None and surname_element is not None:
            forename = forename_element.text.strip()
            surname = surname_element.text.strip()
            cited_authors.append(f"{forename} {surname}")
    return cited_authors

output_folder = './output/authors_citations'
input_folder = './output/GrobidOutput/publications'

if not os.path.exists(output_folder):
    os.makedirs(output_folder)
process_xml_files(output_folder, input_folder)
