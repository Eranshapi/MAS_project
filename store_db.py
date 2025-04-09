import os
from dotenv import load_dotenv
from extract_text import extract_text_from_folder
from preprocess import preprocess_text, split_text_into_chunks
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()

# Paths
data_path = "data"
chroma_path = "chroma_db"

# Extract text from files
text_data = extract_text_from_folder(data_path)
print(f"Extracted text data: {text_data[:5]}")  # Print the first 5 items to check

# Preprocess text
cleaned_text = [clean_text(txt) for txt in text_data]
chunks = split_text_into_chunks(cleaned_text)

# Initialize HuggingFace Embeddings
embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
embeddings = embeddings_model.embed_documents(cleaned_text)
print(f"Generated embeddings: {embeddings[:5]}")  # Print the first 5 embeddings to check

# Store in ChromaDB (auto-persist)
vector_db = Chroma.from_documents(chunks, embedding=embeddings_model, persist_directory=chroma_path)

print(vector_db)

print("ChromaDB created successfully at:", chroma_path)
print(f"Total Chunks Stored: {len(texts)}")
