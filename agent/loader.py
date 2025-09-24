# agent/loader.py
import os
from typing import List
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader

SUPPORTED = [".pdf", ".txt", ".md"]

def load_from_path(path: str) -> List[Document]:
    """
    If path is file: load that file.
    If path is directory: load all supported files inside.
    Returns list of Document objects.
    """
    docs = []
    if os.path.isfile(path):
        docs.extend(_load_file(path))
    elif os.path.isdir(path):
        for f in sorted(os.listdir(path)):
            p = os.path.join(path, f)
            if os.path.isfile(p) and os.path.splitext(p)[1].lower() in SUPPORTED:
                docs.extend(_load_file(p))
    else:
        raise ValueError(f"Path not found: {path}")
    return docs

def _load_file(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(path)
        return loader.load()
    elif ext in [".txt", ".md"]:
        loader = TextLoader(path, encoding="utf-8")
        return loader.load()
    else:
        return []

def chunk_docs(docs, chunk_size: int = 500, chunk_overlap: int = 50):
    """
    docs: list of langchain Document objects (with .page_content)
    returns: list of Document chunks
    """
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(docs)
