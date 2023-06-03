# This file has ingestion related logic. 
# loads markdown files an makes them into a vector store that we can use. 

import os
import pickle

from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS


def find_files_with_extension(directory, extension):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                file_paths.append(os.path.join(root, file))
    return file_paths

def ingest_docs():
    directory = "./frontend/src/assets/posts"  # Replace with the actual directory path
    extension = '.md'

    md_files = find_files_with_extension(directory, extension)

    all_docs = []

    for file in md_files:
        loader = UnstructuredMarkdownLoader(file ) #TODO: mode="elements"
        data = loader.load()
        for d in data:
            all_docs.append(d)

    print(f'Total number of elements: {len(all_docs)}')


    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )
    split_docs = text_splitter.split_documents(all_docs)
    print(f'Number of docs after splitting: {len(split_docs)}')
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    # Save vectorstore
    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)


if __name__ == "__main__":
    ingest_docs()