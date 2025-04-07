import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

def clean_text(text):
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra spaces
    return text

def split_text_into_chunks(text_data, chunk_size=500, overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    docs = text_splitter.split_text("\n".join(text_data))
    return docs
