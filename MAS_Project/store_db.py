import os
from dotenv import load_dotenv
from extract_text import extract_text_from_folder
from preprocess import clean_text, split_text_into_chunks
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

# Load environment variables
load_dotenv()

# Paths
data_path = r"C:\Users\erans\.cursor\MAS_Project\data"
chroma_path = r"C:\Users\erans\.cursor\MAS_Project\chroma_db"

# Extract text from files
text_data = extract_text_from_folder(data_path)

# Preprocess text
cleaned_text = [clean_text(txt) for txt in text_data]
chunks = split_text_into_chunks(cleaned_text)

# Initialize HuggingFace Embeddings
embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Store in ChromaDB (auto-persist)
vector_db = Chroma.from_texts(chunks, embedding=embeddings_model, persist_directory=chroma_path)

print(vector_db)

print("ChromaDB created successfully at:", chroma_path)
 # test