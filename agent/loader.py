# agent/loader.py
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def load_docs(path="data"):
    docs = []
    for file in os.listdir(path):
        if file.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(path, file))
            docs.extend(loader.load())
        elif file.endswith(".md") or file.endswith(".txt"):
            loader = TextLoader(os.path.join(path, file))
            docs.extend(loader.load())
    return docs

def chunk_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return splitter.split_documents(docs)
