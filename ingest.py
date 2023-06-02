# This file has ingestion related logic. 
# loads markdown files an makes them into a vector store that we can use. 

from langchain.document_loaders import UnstructuredMarkdownLoader
import os

def find_files_with_extension(directory, extension):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                file_paths.append(os.path.join(root, file))
    return file_paths

directory = "./frontend/src/assets/posts"  # Replace with the actual directory path
extension = '.md'

md_files = find_files_with_extension(directory, extension)

for file in md_files:
    loader = UnstructuredMarkdownLoader(file, mode="elements")
    data = loader.load()
    for d in data:
        print(d)