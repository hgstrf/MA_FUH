import os
import random
import shutil

input_folder = './co_citation_input/'
N=50

random.seed(42) 

output_folder = f'./co_citation_input_{N}_docs/'

os.makedirs(output_folder, exist_ok=True)
subfolders = [f for f in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, f))]
selected_subfolders = random.sample(subfolders, N)

for subfolder in selected_subfolders:
    src_path = os.path.join(input_folder, subfolder)
    dst_path = os.path.join(output_folder, subfolder)
    shutil.copytree(src_path, dst_path)

print(f'Successfully created {output_folder} with {N} randomly selected subfolders.')
