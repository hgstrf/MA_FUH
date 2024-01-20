import requests
from bs4 import BeautifulSoup
import os
import re
from tqdm import tqdm
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import threading
import sys
import io


window = tk.Tk()
window.title("API Downloader")
window.geometry("400x600") 


class IORedirector(object):
    def __init__(self, text_area):
        self.text_area = text_area


class StdoutRedirector(IORedirector):
    def write(self, str):
        self.text_area.insert(tk.END, str)
        self.text_area.see(tk.END)

# sanitizing to prevent accents or weird symbols
def sanitize_filename(name):
    sanitized_name = re.sub(r"[^\w\-_. ]", "", name)
    sanitized_name = sanitized_name.replace(" ", "_")
    return sanitized_name

def download_pdf(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

def download_click():
    threading.Thread(target=download_click_thread).start()


def download_click_thread():
    download_type = download_type_var.get()

    keywords = keywords_entry.get()
    if keywords == "":
        keywords = "natural language processing"  # default value

    max_results = max_results_entry.get()
    if max_results == "":
        max_results = "50"  # shouldnt be chosen too large as default

    print(f"Starting download with keywords = {keywords}")

    output_directory = filedialog.askdirectory()

    selected_api = api_var.get()

    base_url = ""

    if selected_api == "ArXiv":
        base_url = "http://export.arxiv.org/api/query?"     # can be changed or new APIs can be included here
    elif selected_api == "TBD":
        print("The selected API is not available.")
        return

    directories = []
    if download_type in ["Author information", "Both"]:
        directories.append(os.path.join(output_directory, "txt"))
    if download_type in ["PDF", "Both"]:
        directories.append(os.path.join(output_directory, "pdf"))
    for directory in directories:
        if os.path.exists(directory):
            files = os.listdir(directory)
            for file in files:
                file_path = os.path.join(directory, file)
                os.remove(file_path)
        else:
            os.makedirs(directory)

    request_url = f"{base_url}search_query=all:{keywords}&max_results={max_results}"

    response = requests.get(request_url)

    soup = BeautifulSoup(response.text, "xml")
    records = soup.find_all("entry")

    for i, record in enumerate(records):
        authors = record.find_all("author")
        authors_list = [author.find('name').text for author in authors]
        if download_type in ["PDF", "Both"]:
            paper_pdf_url = record.find("link", {"title": "pdf"})["href"]
            pdf_filename = os.path.join(
                output_directory, "pdf", f"{paper_pdf_url.split('/')[-1]}.pdf")
            download_pdf(paper_pdf_url, pdf_filename)

        if download_type in ["Author information", "Both"]:
            for author in authors_list:
                sanitized_author = sanitize_filename(author)
                txt_filename = f"{sanitized_author}.txt"
                txt_filepath = os.path.join(
                    output_directory, "txt", txt_filename)

                with open(txt_filepath, "w", encoding="utf-8") as txt_file:
                    txt_file.write("Publication ID:\n")
                    txt_file.write(record.find("id").text + "\n")

                    txt_file.write("\nCo-Authors:\n")
                    for co_author in authors_list:
                        if co_author != author:
                            txt_file.write(co_author + "\n")

        print(f"Downloaded {i+1}/{len(records)}")

    num_files = len(records)
    output_location = os.path.abspath(output_directory)
    print(
        f"Finished downloading. Saved {num_files} files to {output_location}")


# api selector via dropdown
api_label = tk.Label(window, text="API:")
api_label.pack()
api_var = tk.StringVar()
api_dropdown = ttk.Combobox(window, textvariable=api_var, state="readonly")
api_dropdown['values'] = ("ArXiv", "TBD")
api_dropdown.current(0)
api_dropdown.pack()

# download type via dropdown
download_type_label = tk.Label(window, text="Download Type:")
download_type_label.pack()
download_type_var = tk.StringVar()
download_type_dropdown = ttk.Combobox(
    window, textvariable=download_type_var, state="readonly")
download_type_dropdown['values'] = ("Author information", "PDF", "Both")
download_type_dropdown.current(1)  # Set default download type to PDF
download_type_dropdown.pack()

# textbox for keywords
keywords_label = tk.Label(window, text="Keywords:")
keywords_label.pack()
keywords_entry = tk.Entry(window)
keywords_entry.pack()
# default keyword
keywords_entry.insert(tk.END, "natural language processing")

# textbox for max results
max_results_label = tk.Label(window, text="Max Results:")
max_results_label.pack()
max_results_entry = tk.Entry(window)
max_results_entry.pack()
max_results_entry.insert(tk.END, "50")  # Set default max results

# download button
download_button = tk.Button(window, text="Download", command=download_click)
download_button.pack()

console = tk.Text(window)
console.pack(fill=tk.BOTH, expand=True)
sys.stdout = StdoutRedirector(console)

window.mainloop()
