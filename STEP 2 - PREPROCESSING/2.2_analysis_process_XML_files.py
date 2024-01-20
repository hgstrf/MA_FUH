import os
import xml.etree.ElementTree as ET
import re
from tqdm import tqdm
from collections import defaultdict

def sanitize_filename(name, max_length=100):
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    if len(name) > max_length:
        name = name[:max_length]
    return name

def is_valid_name(name):
    pattern = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚàèìòùÀÈÌÒÙäëïöüÄËÏÖÜâêîôûÂÊÎÔÛçñßÇÑ \-\'\.]+$') # allows special characters like "Umlaute" or accents
    return bool(pattern.match(name))


def process_xml_files(input_folder, output_base_folder='./output/co_citation_input'):
    xml_files = [f for f in os.listdir(input_folder) if f.endswith(".xml")]
    for filename in tqdm(xml_files, desc="Processing XML Files"):
        file_path = os.path.join(input_folder, filename)
        tree = ET.parse(file_path)
        root = tree.getroot()
        data = extract_publications_and_authors(root)

        # create unique folder for each publication
        publ_folder = os.path.join(output_base_folder, os.path.splitext(filename)[0])
        if not os.path.exists(publ_folder):
            os.makedirs(publ_folder)

        save_publications_to_files(data, publ_folder)

def calculate_citations(root):            
    cited_authors = []
    citation_elements = root.findall('.//{http://www.tei-c.org/ns/1.0}text/{http://www.tei-c.org/ns/1.0}back/{http://www.tei-c.org/ns/1.0}div/{http://www.tei-c.org/ns/1.0}listBibl/{http://www.tei-c.org/ns/1.0}biblStruct/{http://www.tei-c.org/ns/1.0}analytic/{http://www.tei-c.org/ns/1.0}author')
          
def extract_publication_titles(root):
    publication_titles = []
    citation_elements = root.findall(
        './/{http://www.tei-c.org/ns/1.0}text/{http://www.tei-c.org/ns/1.0}back/{http://www.tei-c.org/ns/1.0}div/{http://www.tei-c.org/ns/1.0}listBibl/{http://www.tei-c.org/ns/1.0}biblStruct/{http://www.tei-c.org/ns/1.0}analytic/{http://www.tei-c.org/ns/1.0}title')
    for citation_element in citation_elements:
        if citation_element.text:
            publication_title = citation_element.text.strip()
            publication_titles.append(publication_title)
    #print(publication_titles)
    return publication_titles
    
def extract_publications_and_authors(root):
    publications = []
    citation_elements = root.findall(
        './/{http://www.tei-c.org/ns/1.0}text/{http://www.tei-c.org/ns/1.0}back/{http://www.tei-c.org/ns/1.0}div/{http://www.tei-c.org/ns/1.0}listBibl/{http://www.tei-c.org/ns/1.0}biblStruct')
    
    for citation_element in citation_elements:
        title_element = citation_element.find('.//{http://www.tei-c.org/ns/1.0}analytic/{http://www.tei-c.org/ns/1.0}title')
        author_elements = citation_element.findall('.//{http://www.tei-c.org/ns/1.0}analytic/{http://www.tei-c.org/ns/1.0}author')
        
        title = title_element.text.strip() if title_element is not None and title_element.text is not None else "Unknown Title"
        authors = []
        for author in author_elements:
            forename_element = author.find('.//{http://www.tei-c.org/ns/1.0}forename')
            surname_element = author.find('.//{http://www.tei-c.org/ns/1.0}surname')
            if forename_element is not None and forename_element.text and surname_element is not None and surname_element.text:
                forename = forename_element.text.strip()
                surname = surname_element.text.strip()
                authors.append(f"{forename} {surname}")

        publications.append((title, authors))
    #print(publications)
    return publications


def save_publications_to_files(publications, output_dir):
    for title, authors in publications:
        safe_title = sanitize_filename(title)  
        filename = f"{safe_title}.txt"
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            for author in authors:
                file.write(author + '\n')

input_folder = './output/GrobidOutput/publications'
process_xml_files(input_folder)

