import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk  # For the Checkbutton widget
import threading
import random
import sys

crawling_stopped = False  # global variable to control the crawling state


def download_file(url, directory, current_page, depth):
    global crawling_stopped
    if crawling_stopped:
        return
    response = requests.get(url)
    filename = os.path.basename(urlparse(url).path)
    filepath = os.path.join(directory, filename)

    if os.path.exists(filepath):
        window.after(0, console_text.insert, tk.END,
                     f"[Depth {depth}] File '{filename}' already exists. Skipping download.\n")
        console_text.see(tk.END)  # Scroll down to the last line
        return

    with open(filepath, 'wb') as file:
        file.write(response.content)
    window.after(0, console_text.insert, tk.END,
                 f"[Depth {depth}] Downloaded from '{current_page}': {filepath}\n")
    console_text.see(tk.END)  # Scroll down to the last line


def is_pdf_link(url):
    return url.endswith('.pdf')


def stop_crawling():
    global crawling_stopped
    crawling_stopped = True
    progress_text.set("Web crawling stopped.")
    console_text.insert(tk.END, "Stopping crawler...\n")
    console_text.see(tk.END)  # Scroll down to the last line


def crawl_wikipedia(start_url, target_directory, max_depth=3, save_frequency=10):
    global crawling_stopped
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    visited_urls = set()
    visited_pages = set()
    stack = [(start_url, 0)]  # Tuple of URL and depth

    def is_stack_full():
        return len(stack) >= 1000

    def update_progress():
        if stack:
            progress_text.set("Crawling... Please wait.")
        else:
            progress_text.set("Web crawling completed.")

    def process_stack():
        while stack and not crawling_stopped:
            current_url, depth = stack.pop()

            # Print the size of the stack
            print(f"Stack size: {len(stack)}")

            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)

            if depth > max_depth:
                continue

            try:
                response = requests.get(current_url)
                soup = BeautifulSoup(response.text, 'html.parser')

                page_links = []  # New list to store links of the current page

                for link in soup.find_all('a'):
                    href = link.get('href')
                    if href:
                        absolute_url = urljoin(current_url, href)
                        if absolute_url not in visited_urls:
                            if is_pdf_link(absolute_url):
                                download_file(
                                    absolute_url, target_directory, current_url, depth)
                            else:
                                # Add link to the page_links list
                                page_links.append(absolute_url)

                # Add links of the current page to the stack in reverse order
                for link in reversed(page_links):
                    if (not is_stack_full()) and (link not in visited_urls):  # Check if the stack is full
                        if depth < max_depth+1:
                            stack.append((link, depth + 1))
                    else:
                        window.after(0, console_text.insert, tk.END,
                                     f"{'─' * 30}\n{' ' * 6}Stack full.\n{'─' * 30}\n")

                # Shuffle stack every X pages if shuffle_enabled is True
                if shuffle_enabled.get() and len(visited_urls) % 1 == 0:
                    random.shuffle(stack)
                    window.after(0, console_text.insert, tk.END,
                                 f"{'─' * 30}\n{' ' * 6}Shuffled the stack at {len(visited_pages)} pages visited.\n{'─' * 30}\n")
                    console_text.see(tk.END)  # Scroll down to the last line

                visited_pages.add(current_url)
                window.after(0, console_text.insert, tk.END,
                             f"[Depth {depth}] Visited page: {current_url}\n")
                console_text.see(tk.END)  # Scroll down to the last line

                if len(visited_pages) % save_frequency == 0:
                    save_visited_pages(target_directory, visited_pages, stack)

            except requests.exceptions.RequestException:
                window.after(0, console_text.insert, tk.END,
                             f"Failed to access: {current_url}\n")
                console_text.see(tk.END)  # Scroll down to the last line

    # Add starting message to console
    window.after(0, console_text.insert, tk.END, "Starting crawler...\n")

    # if stack not empty
    while stack and not crawling_stopped:
        process_stack()

    # Update the progress label after the crawling process finishes
    update_progress()


def save_visited_pages(target_directory, visited_pages, stack):
    logs_directory = os.path.join(target_directory, 'logs')
    if not os.path.exists(logs_directory):
        os.makedirs(logs_directory)

    filename = os.path.join(logs_directory, 'visited_pages.txt')
    sorted_pages = sorted(visited_pages)
    with open(filename, 'w', encoding='utf-8') as file:  # Specify the encoding as utf-8
        for page in sorted_pages:
            file.write(page + '\n')
    window.after(0, console_text.insert, tk.END,
                 f"Visited pages saved to: {filename}\n")
    console_text.see(tk.END)  # Scroll down to the last line

    stack_filename = os.path.join(
        logs_directory, f'stack_{len(visited_pages)}.txt')
    with open(stack_filename, 'w', encoding='utf-8') as stack_file:  # Specify the encoding as utf-8
        stack_file.write('\n'.join([url for url, _ in stack]))
    window.after(0, console_text.insert, tk.END,
                 f"Stack saved to: {stack_filename}\n")
    console_text.see(tk.END)  # Scroll down to the last line


def select_directory():
    selected_directory = filedialog.askdirectory()
    directory_entry.delete(0, tk.END)
    directory_entry.insert(tk.END, selected_directory)


def start_crawling():
    global crawling_stopped
    crawling_stopped = False  # Reset the crawling state when a new crawl starts
    start_url = url_entry.get()
    target_directory = directory_entry.get()
    max_depth = int(depth_entry.get())
    save_frequency = int(frequency_entry.get())

    if not os.path.exists(target_directory):
        messagebox.showerror("Error", "Invalid target directory.")
        return

    console_text.delete('1.0', tk.END)  # Clear console

    # Create a new thread for the crawling process
    crawl_thread = threading.Thread(target=crawl_wikipedia, args=(
        start_url, target_directory, max_depth, save_frequency))
    crawl_thread.start()


# Create the main window
window = tk.Tk()
window.title("Web Crawler")
window.geometry("600x600")

# Global variable to hold the state of the shuffle check button
shuffle_enabled = tk.BooleanVar()


# URL Label and Entry
url_label = tk.Label(window, text="Start URL:")
url_label.pack()
url_entry = tk.Entry(window, width=50)
# Default value
url_entry.insert(
    tk.END, "https://en.wikipedia.org/wiki/Natural_language_processing")
url_entry.pack()

# Directory Label and Entry
directory_label = tk.Label(window, text="Target Directory:")
directory_label.pack()
directory_entry = tk.Entry(window, width=50)
directory_entry.insert(tk.END, "pdfs")  # Default value
directory_entry.pack()
directory_button = tk.Button(window, text="Select", command=select_directory)
directory_button.pack()

# Depth Label and Entry
depth_label = tk.Label(window, text="Maximum Depth:")
depth_label.pack()
depth_entry = tk.Entry(window, width=10)
depth_entry.insert(tk.END, "3")  # Default value
depth_entry.pack()

# Save Frequency Label and Entry
frequency_label = tk.Label(window, text="Save Frequency:")
frequency_label.pack()
frequency_entry = tk.Entry(window, width=10)
frequency_entry.insert(tk.END, "10")  # Default value
frequency_entry.pack()

# Frame for buttons
button_frame = tk.Frame(window)
button_frame.pack()

# Start Button
start_button = tk.Button(
    button_frame, text="Start Crawling", command=start_crawling)
start_button.pack(side=tk.LEFT, padx=10, pady=10)

# Stop Button
stop_button = tk.Button(
    button_frame, text="Stop Crawling", command=stop_crawling)
stop_button.pack(side=tk.LEFT, padx=10, pady=10)

# checkbox
shuffle_check = ttk.Checkbutton(
    window, text="Randomly pick links from stack", variable=shuffle_enabled)
shuffle_check.pack()

# Progress Label
progress_text = tk.StringVar()
progress_label = tk.Label(window, textvariable=progress_text)
progress_label.pack()

# Console Text Widget
console_frame = tk.Frame(window)
console_frame.pack(fill=tk.BOTH, expand=True)

console_text = tk.Text(console_frame, height=15)
console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


# Scrollbar for the console text widget
console_scrollbar = tk.Scrollbar(console_frame, width=20)
console_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure the scrollbar to work with the console text widget
console_text.configure(yscrollcommand=console_scrollbar.set)
console_scrollbar.configure(command=console_text.yview)


# Create a function for scrolling to the end of the console_text widget
def scroll_to_end():
    console_text.see(tk.END)


# Run the GUI event loop
window.mainloop()
